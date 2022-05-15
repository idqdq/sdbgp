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
        console.log("didmount");
        if (this.getToken()) {
            const isAdmin = await this.isAdmin()
            this.setState(() => ({ isAdmin: isAdmin }));            
        }
    }

    handleTabSelect = (tab) => {
        this.setState(()=>({Tab: tab}));
    }

    setToken = (token) => {
        if (token) {
            localStorage.setItem('token', token)            
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
    

    isAdmin = async () => {
        const data = await fetchWrapper(`${config.apiBasePath}/me`);
        if (data){            
            return data?.is_superuser;
        }
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