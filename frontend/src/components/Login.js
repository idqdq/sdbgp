import React, { useState } from 'react';
import PropTypes from 'prop-types';
import config from '../config'


const _authUser = async (username, password) => {
    //delete this.apiClient.defaults.headers['Authorization'];    

    try {
        const res = await fetch(`${config.apiBasePath}/token`, {
            method: "post",
            body: new URLSearchParams({
                'grant_type': 'password',
                'username': username,
                'password': password,
            })
        });

        if (!res.ok) {
            const message = `An error has occured: ${res.status} - ${res.statusText}`;
  
            throw new Error(message);
        }

        const data = await res.json();
        return JSON.stringify(data);

    } catch (err) {
        alert(err.message);
    }
}


export default function Login({ setToken }) {
    const login_wrapper = {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    }
    const [username, setUserName] = useState();
    const [password, setPassword] = useState();

    const handleSubmit = async e => {
        e.preventDefault();
        console.log(username, password);
        const token = await _authUser(username, password);

        setToken(token);
    }

    return (
        <div style={login_wrapper}>
            <h1>Please Log In</h1>
            <form onSubmit={handleSubmit}>
                <label>
                    <p>Username</p>
                    <input type="text" onChange={e => setUserName(e.target.value)} />
                </label>
                <label>
                    <p>Password</p>
                    <input type="password" onChange={e => setPassword(e.target.value)} />
                </label>
                <div>
                    <button type="submit">Submit</button>
                </div>
            </form>
        </div>
    )
}

Login.propTypes = {
    setToken: PropTypes.func.isRequired
}