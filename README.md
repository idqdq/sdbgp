# SDBGP - app to manage BGP prefixes within the GoBGP RIB

## Purpose: 

Hi. this application is designed to prevent and mitigate DDoS attacks

I have a couple of BGP routers in my site facing the internet.
And, of course, I'm a little worried about what to do if I'm attacked.

I don't care too much about ddos though
the main reason i do this is i think this app is a good idea to master some skills (junior level) to be not only a network engineer but also a software developer ;)

Ok now back to the app:  

the app will help to manage routes and policies by controlling a gobgp daemon
while the daemon will speak to our BGP routers advertising politics we have made

![](docs/sdbgp.png)

this application is designed to prevent and mitigate DDoS attacks using two methods:  
1. rfc5635 - Remote Triggered Black Hole Filtering with Unicast Reverse Path Forwarding (uRPF)  
2. rfc5575 - BGP Flow Spec 

## 1. Unicast prefixes + uRPF (S/RTBH)

The Source Remote Triggered Blackhole (S/RTBH) solution is a legacy variant DDoS mitigation that was specified in RFC 5635
http://tools.ietf.org/html/rfc5635

To prevent a future attack we must prepare our network by putting a static discard route for each of our border routers as well as unicast Remote Path Forwarding (uRPF) on each of their interfaces before an attack takes place.  
In case of attack, we somehow have to figure out the original prefixes from which the attack is performed, and place these prefixes in the router database (RIB)

In the modern world, DDOS attacks became more predictable
Because most attacks are caused by political disagreements and not commercial. Such attacks are more fragmented and bring less damage than those that destined to a particular service
Also we can prevent many attacks by putting prefixes in a list based on the geoIP database

So the app does provide the convinient way to place prefixes into routers RIB. For the S/RTBH case prefixes have only one atribute - the nexthop. That is the very nexthop address that must be discarded on the border routers (border means facing to the internet)

The app's tab destined to that type of mitigation looks like this 
![](docs/app_screen.png)

## 2. FlowSpec

S/RTBH method is pretty simple and it is working but it isn't flexible enough. Modern routers support the more advanced technic - the BGP FlowSpec. FlowSpec provides the possibility to filter out flows based on 5-tuple and/or Layer4 information and besides that it has the advanced filtering action like rate-linit or forwarding to another VRF (for inspection)

note it has some limits. My Cisco 4431 routers have limited capacity of 4K flowspec politics. not bad though

In the beginning I was not going to implement this feature but why not. the goBgp daemon supports FlowSpec and it was looking interesting

the apps flowspec tab looks like this
![](docs/app_screen_fs1.png)

here you can see the app's screen and the router console below that that shows the data between app and a router is consistent

## Deployment
### Prerequisits
the app uses protobuf files that depends on the goBgp version

