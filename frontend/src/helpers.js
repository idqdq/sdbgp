// module with helpers functions

const _refreshPage = () =>{
    // it is used to reload a page if token is expired 
    window.location.reload(); 
}

async function fetchWrapper(url, method, body) {
    // the function wraps the fetch() method with two additional entities
    // pre: added auth header from the token
    // post: error handling

    let auth;
    const requestOptions = {}; 
    const tokenString = localStorage.getItem('token');
    
    if (method)
        requestOptions.method = method;

    if (tokenString) {
        const token = JSON.parse(tokenString);
        auth = token?.access_token;

        if (!!auth) {
            requestOptions.headers = { Authorization: `Bearer ${auth}` };
        }
    }

    if (method && body) {
        requestOptions.headers['Content-Type'] = 'application/json';
        requestOptions.body = JSON.stringify(body);
    }

    const res = await fetch(url, requestOptions);

    try {
        if (!res.ok) {
            if ([401, 403].includes(res.status) && auth) {
                // auto logout if 401 Unauthorized or 403 Forbidden response returned from api                        
                localStorage.removeItem('token');                
                _refreshPage();
            }

            const data = await res.json();
            const message = `An error has occured: ${res.status} - ${data.detail}`;
            throw new Error(message);
        }

        if(res.status!==204) {  //204 means no content so there will be an error if you'd try to call the json() method
            if (res.json) {
                return await res.json();
            }
        }

    } catch (err) {
        alert(err.message);
    }
} 
         
export { fetchWrapper };