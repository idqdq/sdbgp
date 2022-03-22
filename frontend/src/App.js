
import React, { Component } from 'react'
import Table from './Table'
import { OneModal, BulkModal } from './Modal';

const URL = "http://127.0.0.1:8000/px"
class App extends Component {
    state = {
        Data: [],        
        changes: {},
        isOneOpen: false,        
        isBulkOpen: false,        
        isFetching: true,
    }

    loaddata = async () => {
        const response = await fetch(URL);
        const data = await response.json();
        this.setState({ Data: data, changes: {}, isFetching: false })
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
        const { Data, changes } = this.state;
        
        const newData = Data.filter((char, i) => { 
            return i !== index;
        })

        // if you've just created a new prefix and then delete it, no change happened
        const ip = Data[index].ip;
        if (changes[ip]==="new"){
            delete changes[ip];
        }
        else {
            changes[ip] = "del";
        }

        this.setState({ Data: newData, changes: changes })        
    }

    pxEdit = index => {
        this.setState({            
            index: index,
        })        

        this.openOneModal();
    }
    
    handleFormOneSubmit = (px, index) => {
        const { changes } = this.state;
        if (index != null) {
            
            const newData = this.state.Data.slice();
            newData[index] = px; // replace old data with a new one in the array
            
            changes[px.ip] = "edit";
            this.setState({ Data: newData, changes: changes });
        }
        else {
            changes[px.ip] = "new";
            this.setState({ Data: [...this.state.Data, px], changes: changes });
        }
        this.hideOneModal();
    }

    handleFormBulkSubmit = (bulkdata) => {
        this.setState({ Data: [...this.state.Data, bulkdata]});
        this.hideBulkModal();
    }

    handleSubmit = () => {
        const { Data, changes } = this.state;        

        for (let item in changes) {            
            const index = Data.findIndex(x => x.ip===item);            
            const px = Data[index];            

            switch (changes[item]) {              
                case "new":                    
                    this.restPostData(px); 
                    break;

                case "edit":                    
                    this.restPutData(item, px)
                    break;

                case "del":                                        
                    this.restDeleteData(item); 
                    break;

                default:
                    console.log("incorrect value in the changes")
            }
        }
        this.setState({ changes: {}});
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

            const result = {
                status: res.status + "-" + res.statusText,
                headers: {
                    "Content-Type": res.headers.get("Content-Type"),
                    "Content-Length": res.headers.get("Content-Length"),
                },
                data: data,
            };

            alert(JSON.stringify(result, null, 4));
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

                const result = {
                    status: response.status + "-" + response.statusText,
                    headers: { "Content-Type": response.headers.get("Content-Type") },
                    data: data,
                };

                alert(JSON.stringify(result, null, 4));
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

                const result = {
                    status: response.status,                   
                };

                alert(JSON.stringify(result, null, 4));
            } catch (err) {
                alert(err);
            }
        }
    }


    render() {
        const { Data, changes, index, isOneOpen, isBulkOpen } = this.state
        const buttonStyle = {
            margin: '0px 5px',
        }

        return (
            <div className="container">
                <Table Data={Data} changes={changes} pxRemove={this.pxRemove} pxEdit={this.pxEdit}/>
                <div>
                    <button onClick={this.openOneModal} style={buttonStyle} type="button" className="btn btn-outline-primary">New Prefix</button>
                    <button onClick={this.openBulkModal} style={buttonStyle} type="button" className="btn btn-outline-primary">Bulk Load</button>
                    <button onClick={this.loaddata} style={buttonStyle} type="button" className="btn btn-outline-secondary">ReLoad</button>
                    <button onClick={this.handleSubmit} disabled={Object.keys(changes).length===0} style={buttonStyle} type="button" className="btn btn-outline-danger">Submit</button>
                </div>
                <OneModal Data={Data} changes={changes} index={index} isOpen={isOneOpen} hideModal={this.hideOneModal} handleFormSubmit={this.handleFormOneSubmit}/>                           
                <BulkModal isOpen={isBulkOpen} hideModal={this.hideBulkModal} handleFormSubmit={this.handleFormBulkSubmit}/>                           
            </div>
        )
    }
}

export default App