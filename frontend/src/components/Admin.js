import React, { useState } from 'react';
import { logOut } from '../helpers';

export default function Admin(){

    const handleSubmitLogOut = async e => {
        e.preventDefault();        
        logOut();  
        window.location.reload();   
    }    

    const [username, setUserName] = useState();
    const [password, setPassword] = useState();
    const [err, setErr] = useState(false);

    const handleSubmitNewUser = async e => {
        e.preventDefault();         
    }

    return (
        <>
        <div>
            <input type="button" value="LogOut" onClick={handleSubmitLogOut} className="btn btn-outline-success" />
        </div>
        <hr></hr>
        <div>
            <h3>New User</h3>
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
                    <input type="button" value="Submit" onClick={handleSubmitNewUser} className="btn btn-outline-success" />
                    { err && <div style={{color: "red"}}>Incorrect username or password</div>}
            </form>
        </div>
        </>
    )
}