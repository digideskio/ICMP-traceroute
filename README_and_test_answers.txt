********************  README  ********************









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