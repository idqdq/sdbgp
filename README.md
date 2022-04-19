# SDBGP - app to manage BGP prefixes within the GoBGP RIB

## Purpose: 

Hi. this application is designed to help prevent and mitigate DDoS attacks

I have a couple of BGP routers in my site facing the internet.
And, of course, I'm a little worried about what to do if I'm attacked.

I don't care too much about ddos though
the main reason i do this is i think this app is a good idea to master some skills (junior level) to be not only a network engineer but also a software developer ;)

Ok now back to the app:  

the app will help to manage routes and policies by controlling a gobgp daemon
while the daemon will speak to our BGP routers advertising politics we have made

this application is designed to prevent and mitigate DDoS attacks using two methods:  
1. rfc5635 - Remote Triggered Black Hole Filtering with Unicast Reverse Path Forwarding (uRPF)  
2. rfc5575 - BGP Flow Spec 

## 1. Unicast prefixes + uRPF (S/RTBH)

On the first glance this method works pretty much like a simple ACL or firewall filtering  
but it would become a tedious task if you have to deal with couple of thousands prefixes. 


## 2. FlowSpec

S/RTBH method is pretty simple and it is working but it isn't flexible enough  
so we'll be dealing with the advanced method: BGP FlowSpec 
with flowspec we can match flows on 5-tuple and Layer 4 traffic properties
it has its limits though. My Cisco 4431 routers have limited capacity of 4K flowspec politics


## Prerequisits
the app uses protobuf files that depends on the goBgp version

