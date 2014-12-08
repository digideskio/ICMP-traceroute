********************  README  ********************
nobody ever responds with an ICMP response of 0, and that makes me sad.
the only responses, the entire time I was writing this project, were 3 or 11.

Regardless, 'sudo python ./rttMeasurement.py' seems to work how I would like it to.
Yeah, I switched around what IPs I'm testing it on, but that's because nobody plays nice.  This is noted in the
assignment, and the traceroute run against the 9th IP in the list shows this behaviour.
No ICMP response 3 is ever given.  So I used this as a sample to show a ABSOLUTE_MAX_TTL value.

So test 9 will take some time as you wait for the last several hops to timeout.


********************  Text Answers  ********************
-TTL is too small if the destination host isn't reached by the time the packet is dropped

-TTL is too large if a response from the desired host is received.  This can be tricky because this is also
    the case if the TTL is at the correct number

-ICMP probes can be matched with responses by writing your own packet header, and comparing the received header

-Reasons for not receiving a response,
 taken from http://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Control_messages
    Destination network unreachable
    Destination host unreachable
    Destination protocol unreachable
    Destination port unreachable
    Fragmentation required, and DF flag set
    Source route failed
    Destination network unknown
    Destination host unknown
    Source host isolated
    Network administratively prohibited
    Host administratively prohibited
    Network unreachable for TOS
    Host unreachable for TOS
    Communication administratively prohibited
    Host Precedence Violation
    Precedence cutoff in effect
    TTL expired
    defragmentation time exceeded


I included the sample run I used to compile "Ping dataset" in the text file "source_dataset.txt"
    The conclusions to draw are pretty clear: increases in RTT generally linearly increase with the number of hops
        Geographic distance is typically impacts RTT more than anything else (that darn speed of light)
        Jitter within the RTT is easily observed at the lower hops