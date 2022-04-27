import React, { useState } from 'react';
import { Modal } from "react-bootstrap";
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
            const data = await res.json();
            const message = `An error has occured: ${res.status} - ${data.detail}`;            
            throw new Error(message);
        }

        const data = await res.json();
        return JSON.stringify(data);

    } catch (err) {
        alert(err.message);
    }
}


export default function Login({ setToken }) {

    const [username, setUserName] = useState();
    const [password, setPassword] = useState();

    const handleSubmit = async e => {
        e.preventDefault();        
        const token = await _authUser(username, password);
        if (token)
            setToken(token);
    }

    return (
        <Modal show={true} fullscreen={true} >
            <Modal.Header>
                <Modal.Title>Please Login</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <form>
                    <div className="mb-3 row">
                        <label htmlFor="login" className="col-sm-2 col-form-label">login</label>
                        <div className="col-sm-10">
                            <input
                                className="form-control"
                                name="login"
                                type="text"
                                id="login_id"
                                value={username || ''}
                                onChange={e => setUserName(e.target.value)}
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="password" className="col-sm-2 col-form-label">password</label>
                        <div className="col-sm-10">
                            <input
                                className="form-control"
                                type="password"
                                name="password"
                                value={password || ''}
                                onChange={e => setPassword(e.target.value)}
                            />
                        </div>
                    </div>
                    <input type="button" value="Submit" onClick={handleSubmit} className="btn btn-outline-success" />
                </form>
            </Modal.Body>
        </Modal>
    )
}


Login.propTypes = {
    setToken: PropTypes.func.isRequired
}

//const tokenString = localStorage.getItem('token');
//atob(JSON.parse(tokenString).access_token.split('.')[1])
//{\"type\":\"access_token\",\"exp\":1651761461,\"iat\":1651070261,\"sub\":\"admin\"}