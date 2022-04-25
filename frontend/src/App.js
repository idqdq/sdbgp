import React, { Component } from 'react'
//import config from './config'
import AppTabs from './components/Tabs';
import Bgp from './components/Bgp';
import Login from './components/Login';


class App extends Component {
    state = {
        Tab: 'unicast',
        token: null,
    }
    
    handleTabSelect = (tab) => {
        this.setState(()=>({Tab: tab}));
    }

    setToken = (token) => {
        sessionStorage.setItem('token', token)
        this.forceUpdate(); // rerender component after successfull login
    }

    getToken = () => {
        const tokenString = sessionStorage.getItem('token');
        const token = JSON.parse(tokenString);
        return token?.access_token;        
    }

    render() {
        
        const token = this.getToken();

        if(!token) {
          return <Login setToken={this.setToken} />
        }

        return (                        
            <div className="container">
                <AppTabs onSelect={this.handleTabSelect} activeKey={this.state.Tab}/>
                { (this.state.Tab === 'unicast' || this.state.Tab === 'flowspec') && <Bgp Tab={this.state.Tab}/> }
                { this.state.Tab === 'logging' && <h3>logging</h3>}
                { this.state.Tab === 'help' && <h3>help</h3>}
                       
            </div>
        )
    }
}

export default App