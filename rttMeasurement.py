# TODO: actually use the ABSOLUTE_MAX_TTL
# TODO: finish writing and debugging the new binary search implementation
# adapted from          https://github.com/ashabbir/Traceroute/blob/master/icmppinger.py
# with more help from   https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your
# and from              http://en.wikipedia.org/wiki/Binary_search_algorithm#Iterative

from socket import *
import socket
import os
import sys
import struct
import time
import select

TIMEOUT = 2.0
TRIES = 2
ABSOLUTE_TTL_MAX = 255
DEBUG_MODE = 1


def main():
    ip = socket.gethostbyname("cwru.edu")
    binary_traceroute(ip)
    # with open('targets.txt') as file_name:
    # ips = file_name.readlines()
    #     for i in ips:
    #         binary_traceroute(i.strip('\n'))


# calculates the checksum of the packet, returns the checksum
def checksum(given_string):
    checksum_val = 0
    count_upper_bound = (len(given_string) / 2) * 2
    count = 0
    while count < count_upper_bound:
        current_value = ord(given_string[count + 1]) * 256 + ord(given_string[count])
        count += 2
        checksum_val += current_value
        checksum_val &= 0xffffffffL
    if count_upper_bound < len(given_string):
        checksum_val += ord(given_string[len(given_string) - 1])
        checksum_val &= 0xffffffffL
    checksum_val = (checksum_val >> 16) + (checksum_val & 0xffff)
    checksum_val += (checksum_val >> 16)
    answer = ~checksum_val
    answer &= 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


# builds a packet, with checksum, returns the created packet
def build_packet():
    checksum_val = 0
    header = struct.pack("bbHHh", 8, 0, checksum_val, os.getpid() & 0xFFFF, 1)
    data = struct.pack("d", time.time())
    checksum_val = checksum(header + data)
    if sys.platform == 'darwin':
        checksum_val = socket.htons(checksum_val) & 0xffff
    else:
        checksum_val = socket.htons(checksum_val)
    header = struct.pack("bbHHh", 8, 0, checksum_val, os.getpid() & 0xFFFF, 1)
    packet = header + data
    return packet


# gets the hostname of a given IP, returns the hostname
def get_name(host_ip):
    try:
        host = socket.gethostbyaddr(host_ip)
        name = '{0} ({1})'.format(host_ip, host[0])
    except Exception:
        name = '{0} (host name could not be determined)'.format(host_ip)
    return name


# gets the route to a host, resolving nodes along the way traceroute-style
def probe(ip, ttl):
    time_remaining = TIMEOUT
    return_array = []
    icmp_type = -1
    for tries in xrange(TRIES):
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname("udp"))
        send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
        send_socket.settimeout(TIMEOUT)
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        recv_socket.settimeout(TIMEOUT)
        try:
            send_socket.sendto(build_packet(), (ip, 33434))
            t = time.time()
            is_timeout = select.select([recv_socket], [], [], time_remaining)
            time_in_select = (time.time() - t)
            if not is_timeout[0]:  # changed from == []
                return_array.append(" A Timeout occurred  (type 1)")
            received_packet, address = recv_socket.recvfrom(1024)
            time_received = time.time()
            time_remaining -= time_in_select
            if time_remaining <= 0:
                return_array.append(" A Timeout occurred  (type 2)")
        except timeout:
            return_array.append(" A Timeout occurred  (type 3)")
            return return_array, 11
        else:
            icmp_header_content = received_packet[20:28]  # grab the header from the packet
            # unpack the ICMP header: unsigned short, unsigned short, signed short
            icmp_type, a, b, c, d = struct.unpack("bbHHh", icmp_header_content)
            readable_name = get_name(address[0])
            if icmp_type == 11:  # time exceeded
                return_array.append("11:  %d rtt=%.0f ms %s" % (ttl, (time_received - t) * 1000, readable_name))
            elif icmp_type == 3:  # destination unreachable, interpreted as success, oddly enough
                return_array.append("03:  %d    rtt=%.0f ms    %s" % (ttl, (time_received - t) * 1000, readable_name))
            elif icmp_type == 0:  # echo reply, doesn't really happen
                packet_bytes = struct.calcsize("d")
                time_sent = struct.unpack("d", received_packet[28:28 + packet_bytes])[0]
                return_array.append("00:  %d rtt=%.0f ms %s" % (ttl, (time_received - time_sent) * 1000, readable_name))
                return
            else:
                return_array.append(" A Timeout occurred  (type 4)")
            break
        finally:
            send_socket.close()
    return return_array, icmp_type


def get_ip(hostname):
    return socket.gethostbyname(hostname)


# runs a traceroute against the host_name, using a binary search to calculate the optimal TTL
# algorithm adapted from: http://en.wikipedia.org/wiki/Binary_search_algorithm#Iterative
def binary_traceroute(host_ip):
    rapid_increase_phase = 1
    ttl_ub = 16  # initialized to an invalid value
    ttl_lb = 0
    ttl_current = 16
    print "**********BEGIN BINARY SEARCH PHASE**********"
    while ttl_ub - ttl_lb > 1 or rapid_increase_phase:
        _, icmp_value = probe(host_ip, ttl_current)
        if DEBUG_MODE:
            print "probed %s with %d hops, returning an icmp of %s" % (host_ip, ttl_current, icmp_value)
        # icmp_value of 3 (dest_unreachable) indicates ttl was too high, OR just right (tricky)
        # icmp_value of 11 (ttl_expired) indicates ttl was too low, and packet was dropped before destination
        if icmp_value is 11 and rapid_increase_phase is 1:
            ttl_lb = ttl_current*2
            ttl_ub *= 2
            if ttl_ub >= ABSOLUTE_TTL_MAX:
                ttl_ub = ABSOLUTE_TTL_MAX
                print "TTL Maximum exceeded!"
                break
            # todo: use the absolute max_ttl
        elif icmp_value is 11:
            ttl_lb = ttl_current
            # ttl_ub = (ttl_lb + ttl_ub) / 2
        elif icmp_value is 3:
            rapid_increase_phase = 0
            ttl_ub = ttl_current
            # ttl_lb = (ttl_lb + ttl_ub) / 2
        ttl_current = (ttl_lb + ttl_ub) / 2
    print "**********END BINARY SEARCH PHASE**********"
    # exited while loop, run the traceroute with ttl_ub.
    print "ICMP_Value  Hop_number  rtt  host_IP(hostname)"
    for i in xrange(1, ttl_ub+1):
        output, _ = probe(host_ip, i)
        print output[0]

if __name__ == '__main__':
    main()
