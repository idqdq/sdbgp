# frontend for my sdbgp app

this is a React.js application.  
the goal of the app is to manipulate RIB routes for the [goBGP](https://github.com/osrg/gobgp) instance  

1. frontend must be started after the backend is started  
2. if you plan to run it not only on localhost, you must notify the application about the address of the backend, and also tell the backend about the CORS parameters.

----
note: to start the front first install all the node modules by typing  
> \> npm install app

and then type:  
> \> npm start

this would run the app in a localhost (dev) mode  


to deploy it for production purposes (not localhost) we need to tell  the app of the backend address to pass CORS check of a browser.  
**REACT_APP_API_BASE_PATH** is the environment variable  
assuming that the address *10.1.2.3:8001 is* your backend server IP type these commands:
> \> export REACT_APP_API_BASE_PATH='http://10.1.2.3:8001'  
> \> npm start  


and if it runs successfully compile the app by typing the commands:
> \> export REACT_APP_API_BASE_PATH='http://10.1.2.3:8001'  
> \> npm run build

when the build has been done run the app with:
> \> serve -s build &


the CORS params related to the backend deplyment