import React, { Component } from 'react'
import config from './config'
import AppTabs from './components/Tabs';
import Bgp from './components/Bgp';
import Login from './components/Login';
import Admin from './components/Admin';
import { fetchWrapper } from './helpers';

class App extends Component {
    state = {
        Tab: 'unicast',            
        isAdmin: false,   
    }    

    async componentDidMount(){        
        if (this.getToken()) {   
            await this.setUser();                             
        }
    }

    setToken = async (token) => {
        if (token) {
            localStorage.setItem('token', token)
            await this.setUser();

            this.forceUpdate(); // rerender component after successfull login
        }
    }

    getToken = () => {
        const tokenString = localStorage.getItem('token');
        if (tokenString) {            
            const token = JSON.parse(tokenString);
            return token?.access_token;
        }
    }

    _fetchUser = async () => {
        return await fetchWrapper(`${config.apiBasePath}/me`);   
    }

    setUser = async () => {
        const user = await this._fetchUser(); // user's properties comes from the backend for security purposes
        localStorage.setItem('user', user?.user);
        this.setState(() => ({ isAdmin: user?.is_superuser }));
    }
   
    handleTabSelect = (tab) => {
        this.setState(()=>({Tab: tab}));
    }


    render() {
        
        const token = this.getToken();

        if(!token) {
          return <Login setToken={this.setToken} />
        } 

        return (                        
            <div className="container">
                <AppTabs onSelect={this.handleTabSelect} activeKey={this.state.Tab} isAdmin={this.state.isAdmin}/>
                { (this.state.Tab === 'unicast' || this.state.Tab === 'flowspec') && <Bgp Tab={this.state.Tab}/> }
                { this.state.Tab === 'logging' && <h3>logging</h3>}
                { this.state.Tab === 'help' && <h3>help</h3>}
                { this.state.Tab === 'admin' && <Admin />}
                       
            </div>
        )
    }
}

export default App