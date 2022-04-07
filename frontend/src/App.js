import React, { Component } from 'react'
import Table from './components/Table'
import { FormModal, FormBulkModal, SpinerModal } from './components/Modal';
import AppTabs from './components/Tabs';

const DEBUG = false;

const URL_MONGO_API = {
    unicast: "http://127.0.0.1:8000/mongo/unicast", 
    flowspec: "http://127.0.0.1:8000/mongo/flowspec",
};
const URL_GORIB_API = {
    unicast: "http://127.0.0.1:8000/gobgp/unicast",
    flowspec: "http://127.0.0.1:8000/gobgp/flowspec",
}

class App extends Component {
    state = {
        Tab: 'unicast',
        Data: [],         
        View: [],
        search: '',
        changes: {},
        checkbx: false,
        isFormOpen: false,        
        isBulkOpen: false,           
        isFetching: true,
    }

    loaddata = async (tab=this.state.Tab) => {
        const response = await fetch(URL_MONGO_API[tab]);
        const data = await response.json();
        this.setState({ Data: data, View: data, search: '', changes: {}, isFetching: false, checkbx: false })
    }

    async componentDidMount(){
        await this.loaddata();
    }

    openFormModal = () => {
        this.setState({
            isFormOpen: true
        });        
    }

    hideFormModal = () => {
        this.setState({
            isFormOpen: false
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
            return !(px.src===item.src && px.prefix_len===item.prefix_len);
        })
        const newView = View.filter((char, i) => { 
            return i !== index;
        })

        // if you've just created a new prefix and then delete it, no change happened
        const src = View[index].src;
        if (changes[src]==="new"){
            delete changes[src];
        }
        else {
            changes[src] = "del";
        }

        this.setState({ Data: newData, View: newView, changes: changes })        
    }

    pxEdit = index => {
        this.setState({            
            index: index,
        })        
        this.openFormModal();        
    }
    
    handleTabSelect = (tab) => {
        this.setState(()=>({Tab: tab}));
        this.loaddata(tab);
    }

    handleFormSubmit = (px, viewindex) => {
        const { Data, View, changes } = this.state;
        if (viewindex != null) {             
            const dataindex = Data.indexOf(View[viewindex]); // find Data.index for the old unchanged data
            const newData = Data.slice();
            const newView = View.slice();                                

            newView[viewindex] = px; // replace old data with a new one in the View array
            newData[dataindex] = px; // replace old data with a new one in the Data array
                        
            changes[px.src] = "edit";
            this.setState({ Data: newData, View: newView, changes: changes });
        }
        else {
            changes[px.src] = "new";
            this.setState({ Data: [...Data, px], View: [...View, px], changes: changes });
        }
        this.hideFormModal();
    }

    handleFormBulkSubmit = (bulkdata) => {     
        const { Data } = this.state;    
        const changes = {}

        this.hideBulkModal();
        this.setState(() => ({ isFetching: true }));
        
        const newData = bulkdata.filter((b) => !Data.find((a) => a.src === b.src)); // uniqueness
        newData.forEach(el => changes[el.src] = "new");
        
        const fullData = [...Data, ...newData];
        
        this.setState({ 
            Data: fullData, 
            View: fullData,
            changes: changes,
            isFetching: false,
        });                
    }

    handleSubmit = () => {
        const { Data, changes } = this.state;                
        this.setState(() => ({ isFetching: true }));

        if (Object.keys(changes).length > 10) {
            // bulk processing
            const arrnew = []
            const arredit = []
            const arrdel = []
            
            for (let i in changes){
                switch(changes[i]){
                    case "new":
                        arrnew.push(i);
                        break;

                    case "edit":
                        arredit.push(i);
                        break;

                    case "del":
                        arrdel.push(i);
                        break;
                    default:
                        break;
                }
            }

            function prepareBulkData(arr){
                const BulkData = [];
                arr.forEach((i) => {
                    const index = Data.findIndex(x => x.src === i);
                    BulkData.push(Data[index]);
                })
                return BulkData;
            }

            arrdel.forEach((i) => this.restDelData(i));

            const DataNew = prepareBulkData(arrnew);
            this.restPostData(DataNew, true); // bulk = true

            const DataEdit = prepareBulkData(arredit);
            DataEdit.forEach((px) => this.restPutData(px));
        } 
        else {
            // one_by_one processing 
            for (let i in changes) {
                if (changes[i] === "del") {
                    this.restDelData(i);
                }
                else {
                    const index = Data.findIndex(x => x.src === i);
                    const px = Data[index];

                    if (changes[i] === "new") {
                        this.restPostData(px);
                    }
                    if (changes[i] === "edit") {
                        this.restPutData(px)
                    }
                }
            }
        }
        this.setState({ changes: {}, isFetching: false });
    }

    stripData = (value) => {                
        const View = this.state.Data.filter((item) => item.src.startsWith(value));
        this.setState ({View: View, search: value});
    }

    handleSearchChange = (event) => {
        const { value } = event.target;
        this.stripData(value);
    }

    handleCheckbx = () => {
        this.setState({checkbx: !this.state.checkbx})
    }

    handleDB2RIB = async () => {
        this.setState(() => ({ isFetching: true }));        
        try {
            const res = await fetch(`${URL_GORIB_API[this.state.Tab]}/db2rib`);
            if (!res.ok) {
                const message = `An error has occured: ${res.status} - ${res.statusText}`;
                throw new Error(message);
            }            
            
            this.setState({ isFetching: false, checkbx: false })

        } catch (err) {
            alert(err.message);
        }
        this.setState({ isFetching: false });
    }
    
    handleRIB2DB = async () => {
        this.setState(() => ({ isFetching: true }));
        try {
            const res = await fetch(`${URL_GORIB_API[this.state.Tab]}/rib2db`);
            if (!res.ok) {
                const message = `An error has occured: ${res.status} - ${res.statusText}`;
                throw new Error(message);
            }            
            
            this.loaddata();

        } catch (err) {
            alert(err.message);
        }
        this.setState({ isFetching: false });
    }

    handleClearDB = async () => {
        this.setState(() => ({ isFetching: true }));        
        try {
            const res = await fetch(`${URL_GORIB_API[this.state.Tab]}/cleardb`);
            if (!res.ok) {
                const message = `An error has occured: ${res.status} - ${res.statusText}`;
                throw new Error(message);
            }

            await res.json();
            //alert("DB is empty");
            this.loaddata();

        } catch (err) {
            alert(err.message);
        }
        this.setState({ isFetching: false });
    }

    handleClearRIB = async () => {
        this.setState(() => ({ isFetching: true }));
        try {
            const res = await fetch(`${URL_GORIB_API[this.state.Tab]}/delallrib`);
            if (!res.ok) {
                const message = `An error has occured: ${res.status} - ${res.statusText}`;
                throw new Error(message);
            }

            await res.json();
            this.setState({ isFetching: false, checkbx: false })
            //alert("RIB is empty");

        } catch (err) {
            alert(err.message);
        }        
        this.setState({ isFetching: false });
    }    

    restPostData = async (px, bulk=false) => {
        try {
            const URL = bulk ? `${URL_MONGO_API[this.state.Tab]}/bulk` : `${URL_MONGO_API[this.state.Tab]}`;
            const res = await fetch(URL, {
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
        if (px.src) {
            try {
                const response = await fetch(`${URL_MONGO_API[this.state.Tab]}/${px.src}`, {
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

    restDelData = async (src) => {
        if (src) {
            try {
                const response = await fetch(`${URL_MONGO_API[this.state.Tab]}/${src}`, { method: "delete" });
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
        const { Tab, Data, View, changes, index, isFormOpen, isBulkOpen, search, checkbx, isFetching } = this.state
        
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
        const checkStyle = {
            margin: '0px 10px',
        }           
        const checkLabelStyle = {
            margin: '-20px 20px',
            color: 'purple',
            //fontStyle: 'oblique',  
            opacity: '0.7',          
        }
        return (                        
            <div className="container">
                <AppTabs onSelect={this.handleTabSelect} activeKey={Tab}/>
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
                                style={searchStyle} 
                                disabled={ Data.length > 1000 }/>
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
                    <div>
                        <label>Tab: {Tab}</label>
                    </div>
                </div>
                
                <Table Tab={Tab} Data={View} changes={changes} pxRemove={this.pxRemove} pxEdit={this.pxEdit}/>
                
                <div className="buttons" style={buttonsRowStyle}>                    
                    { Tab === "unicast" && <button onClick={this.openFormModal} style={buttonStyle} type="button" className="btn btn-outline-primary">New Prefix</button> }
                    { Tab === "flowspec" && <button onClick={this.openFormModal} style={buttonStyle} type="button" className="btn btn-outline-primary">New Policy</button>}
                    { Tab === "unicast" && <button onClick={this.openBulkModal} style={buttonStyle} type="button" className="btn btn-outline-primary">Bulk Load</button> }
                    <button onClick={(e) => this.loaddata(Tab, e)} style={buttonStyle} type="button" className="btn btn-outline-secondary">ReLoad</button>
                    <button onClick={this.handleSubmit} disabled={Object.keys(changes).length===0} style={buttonStyle} type="button" className="btn btn-outline-danger">Save to DB</button>                    
                </div>
                <div className="buttons" style={buttonsRowStyle}>
                    <div className="form-floating">                        
                        <input onChange={this.handleCheckbx} style={checkStyle} checked={checkbx} className="form-check-input" type="checkbox" id="checkbox_id" name="checkbx"></input>
                        <label htmlFor="checkbx" style={checkLabelStyle}>enable DB/RIB actions</label>
                    </div>
                    <button onClick={this.handleRIB2DB} disabled={!checkbx} style={buttonStyle} type="button" className="btn btn-outline-dark">{'RIB => DB'}</button>
                    <button onClick={this.handleDB2RIB} disabled={!checkbx || Object.keys(changes).length!==0} style={buttonStyle} type="button" className="btn btn-outline-dark">{'DB => RIB'}</button>
                    <button onClick={this.handleClearDB} disabled={!checkbx} style={buttonStyle} type="button" className="btn btn-outline-dark">Clear DB</button>
                    <button onClick={this.handleClearRIB} disabled={!checkbx} style={buttonStyle} type="button" className="btn btn-outline-dark">Clear RIB</button>
                </div>
                <FormModal Tab={Tab} Data={View} changes={changes} index={index} isOpen={isFormOpen} hideModal={this.hideFormModal} handleFormSubmit={this.handleFormSubmit}/>                           
                <FormBulkModal isOpen={isBulkOpen} hideModal={this.hideBulkModal} handleFormSubmit={this.handleFormBulkSubmit}/>
                <SpinerModal show={isFetching}/>                  
            </div>
        )
    }
}

export default App