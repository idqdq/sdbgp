
import React, { Component } from 'react'
import Table from './Table'
import { OneModal, BulkModal } from './Modal';

const DEBUG = false;
const URL = "http://127.0.0.1:8000/px"
class App extends Component {
    state = {
        Data: [],        
        View: [],
        search: '',
        changes: {},
        isOneOpen: false,        
        isBulkOpen: false,        
        isFetching: true,
    }


    loaddata = async () => {
        const response = await fetch(URL);
        const data = await response.json();
        this.setState({ Data: data, View: data, search: '', changes: {}, isFetching: false })
    }


    async componentDidMount(){
        await this.loaddata();
    }


    openOneModal = () => {
        this.setState({
            isOneOpen: true
        });        
    }


    hideOneModal = () => {
        this.setState({
            isOneOpen: false
        });        
        delete this.state.index;
    }


    openBulkModal = () => {
        this.setState({
            isBulkOpen: true
        });        
    }


    hideBulkModal = () => {
        this.setState({
            isBulkOpen: false
        });                
    }


    pxRemove = index => {
        const { Data, View, changes } = this.state;
        const px = View[index];

        const newData = Data.filter((item) => { 
            return !(px.ip===item.ip && px.mask_cidr===item.mask_cidr);
        })
        const newView = View.filter((char, i) => { 
            return i !== index;
        })

        // if you've just created a new prefix and then delete it, no change happened
        const ip = View[index].ip;
        if (changes[ip]==="new"){
            delete changes[ip];
        }
        else {
            changes[ip] = "del";
        }

        this.setState({ Data: newData, View: newView, changes: changes })        
    }


    pxEdit = index => {
        this.setState({            
            index: index,
        })        

        this.openOneModal();
    }
    

    handleFormOneSubmit = (px, viewindex) => {
        const { Data, View, changes } = this.state;
        if (viewindex != null) {             
            const dataindex = Data.indexOf(View[viewindex]); // find Data.index for the old unchanged data
            const newData = Data.slice();
            const newView = View.slice();                                

            newView[viewindex] = px; // replace old data with a new one in the View array
            newData[dataindex] = px; // replace old data with a new one in the Data array
                        
            changes[px.ip] = "edit";
            this.setState({ Data: newData, View: newView, changes: changes });
        }
        else {
            changes[px.ip] = "new";
            this.setState({ Data: [...Data, px], View: [...View, px], changes: changes });
        }
        this.hideOneModal();
    }


    handleFormBulkSubmit = (bulkdata) => {     
        const { Data } = this.state;      
        const changes = {}

        const newData = bulkdata.filter((b) => !Data.find((a) => a.ip === b.ip)); // uniqueness
        newData.forEach(el => changes[el.ip] = "new");
        
        const fullData = [...Data, ...newData];
        
        this.setState({ 
            Data: fullData, 
            View: fullData,
            changes: changes
        });        
        this.hideBulkModal();
    }


    handleSubmit = () => {
        const { Data, changes } = this.state;        

        for (let ip in changes) {            
            const index = Data.findIndex(x => x.ip===ip);            
            const px = Data[index];            

            switch (changes[ip]) {              
                case "new":                    
                    this.restPostData(px); 
                    break;

                case "edit":                    
                    this.restPutData(px)
                    break;

                case "del":                                        
                    this.restDeleteData(ip); 
                    break;

                default:
                    console.log("incorrect value in the changes")
            }
        }
        this.setState({ changes: {}});
    }

    stripData = (value) => {                
        const View = this.state.Data.filter((item) => item.ip.startsWith(value));
        this.setState ({ View: View, search: value});
    }

    handleSearchChange = (event) => {
        const { value } = event.target;
        this.stripData(value);
    }


    restPostData = async (px) => {
        try {
            const res = await fetch(`${URL}`, {
                method: "post",
                headers: {
                    "Content-Type": "application/json",                    
                },
                body: JSON.stringify(px),
            });

            if (!res.ok) {
                const message = `An error has occured: ${res.status} - ${res.statusText}`;
                throw new Error(message);
            }

            const data = await res.json();

            if (DEBUG) {
                const result = {
                    status: res.status + "-" + res.statusText,
                    headers: {
                        "Content-Type": res.headers.get("Content-Type"),
                        "Content-Length": res.headers.get("Content-Length"),
                    },
                    data: data,
                };
                alert(JSON.stringify(result, null, 4));
            }

        } catch (err) {
            alert(err.message);
        }
    }

    restPutData = async (px) => {
        if (px.ip) {
            try {
                const response = await fetch(`${URL}/${px.ip}`, {
                    method: "put",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(px),
                });

                if (!response.ok) {
                    const message = `An error has occured: ${response.status} - ${response.statusText}`;
                    throw new Error(message);
                }

                const data = await response.json();

                if (DEBUG) {
                    const result = {
                        status: response.status + "-" + response.statusText,
                        headers: { "Content-Type": response.headers.get("Content-Type") },
                        data: data,
                    };
                    alert(JSON.stringify(result, null, 4));
                }
            } catch (err) {
                alert(err)
            }
        }
    }

    restDeleteData = async (ip) => {
        if (ip) {
            try {
                const response = await fetch(`${URL}/${ip}`, { method: "delete" });
                //const data = await response.json();
                if (DEBUG) {
                    const result = {
                        status: response.status,
                    };

                    alert(JSON.stringify(result, null, 4));
                }
            } catch (err) {
                alert(err);
            }
        }
    }


    render() {
        const { Data, View, changes, index, isOneOpen, isBulkOpen, search } = this.state
             
        const searchStyle = {
      //      margin: '20px 0px',
        }
        const search_floater = {
            position: 'sticky',
            top: '20px',          
            left: '20px',   
            margin: '20px 0px',         
        }
        const info_style = {
            position: 'fixed',
            top: '10px',          
            right: '20px',   
            margin: '20px 0px',         
        }
        const buttonStyle = {
            margin: '0px 5px',
        }   
        const buttonsRowStyle = {
            margin: '20px 0px',                        
        }           

        return (            
            <div className="container">
                {/* search box */}                    
                <div className="search" style={search_floater}> <i className="fa fa-search"></i>
                    <div className="input-group">
                        <div className="form-floating">
                            <input type="text"
                                className="form-control"
                                placeholder="Search"
                                name="search"
                                id="search"
                                value={search || ''}
                                onChange={this.handleSearchChange}
                                style={searchStyle} />
                            <label htmlFor="search" style={searchStyle}>Prefix search</label>
                        </div>
                    </div>
                </div>
                <div className="info" style={info_style}>
                    <div>
                        <label htmlFor="search">Total: {Data.length}</label>
                    </div>
                    <div>
                        <label htmlFor="search">In View: {View.length}</label>
                    </div>
                </div>
                
                <Table Data={View} changes={changes} pxRemove={this.pxRemove} pxEdit={this.pxEdit}/>
                
                <div className="buttons" style={buttonsRowStyle}>
                    <button onClick={this.openOneModal} style={buttonStyle} type="button" className="btn btn-outline-primary">New Prefix</button>
                    <button onClick={this.openBulkModal} style={buttonStyle} type="button" className="btn btn-outline-primary">Bulk Load</button>
                    <button onClick={this.loaddata} style={buttonStyle} type="button" className="btn btn-outline-secondary">ReLoad</button>
                    <button onClick={this.handleSubmit} disabled={Object.keys(changes).length===0} style={buttonStyle} type="button" className="btn btn-outline-danger">Submit</button>
                </div>
                <OneModal Data={View} changes={changes} index={index} isOpen={isOneOpen} hideModal={this.hideOneModal} handleFormSubmit={this.handleFormOneSubmit}/>                           
                <BulkModal isOpen={isBulkOpen} hideModal={this.hideBulkModal} handleFormSubmit={this.handleFormBulkSubmit}/>                           
            </div>
        )
    }
}

export default App