# frontend for my sdbgp app

this is a React.js application.  
the goal is to manipulate of RIB routes for the goBGP instance  

the frontend speaks to the back of the app and reflects all the records to the mongo  
when there will be a commit button to send all the routes (via workers) onto the gobgp instance  
probably there will be a calibrate button to fetch all the routes from the RIB to th e mongo  

----
note: to start the front first install all the node modules by typing  
> \> npm install app

and then just type:  
> \> npm start
