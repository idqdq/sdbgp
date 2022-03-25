import React, { Component } from 'react'

//const INTKEYS = ['vlan_id', 'vni', 'mtu'];
//const IPADDRESSKEYS = ['svi_ip', 'mgroup'];

class Form extends Component {
       
    initialState = {
        Data: {
            ip: '',
            mask_cidr: 32,
            next_hop: '',            
        },
        errors: {},
        formValid: false,
    }

    index = this.props.index;        
    state = this.initialState;    

    constructor(props){
        super(props);        
        if (this.index!==undefined) {
            this.state.Data = this.props.Data[this.index];
        }
    }

    handleChange = (event) => {
        const { name, value } = event.target

        this.setState({ 
            Data: { ...this.state.Data, [name]: value }
        })
    }    

    handleBlur = (event) => {
        const { name, value } = event.target
        
        this.validateField(name, value);
        this.isFormValid();        
    }

    isFormValid = () => {
        if (Object.keys(this.state.errors).length === 0) {
            if (this.state.Data.ip && this.state.Data.next_hop) this.setState({ formValid: true });
        }
    }

    submitForm = () => {        
        const data = Object.assign({}, this.state.Data);        

        this.props.handleSubmit(data, this.index);
        this.setState(this.initialState)        
    }

    validateField(name, value){        
        const errors = {};                
        const IpAddrPattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;        

        switch(name) {        
            case 'ip':
                if (value && !IpAddrPattern.test(value)) {
                    errors[name] = 'must be a valid IP address'
                }
                break;          
            case 'mask_cidr':                                
                if(!isNaN(value) && value >=32 && value <= 16) {
                    errors[name] = 'should be a number from 16 to 32';                    
                }          
                break;
            case 'next_hop':
                if (value) {
                    if (!IpAddrPattern.test(value)) {
                        errors[name] = 'must be a valid IP address'
                    }
                }
                break;
            default:
                break;
        }
        
        if (Object.keys(errors).length) {
            this.setState({ errors: {...this.state.errors, ...errors }});
            this.setState({ formValid: false });
        } else {
            if (this.state.errors[name]) {
                let newerrors = { ...this.state.errors };
                delete newerrors[name];
                this.setState({ errors: newerrors });
            }
        }
    }

    render() {
        const { ip, mask_cidr, next_hop } = this.state.Data;

        return (            
            <form>
                <div className="mb-3 row">
                    <label htmlFor="ip" className="col-sm-2 col-form-label">ip</label>
                    <div className="col-sm-10">
                        <input
                            className="form-control"
                            type="text"
                            name="ip"
                            id="ip"
                            value={ip || ''}
                            placeholder="1.2.3.4"
                            onChange={this.handleChange}
                            onBlur = {this.handleBlur} />
                            <span style={{display: "block"}}><small className="form-text text-muted"><i>IPv4 address</i></small></span>
                            <span style={{color: "red"}}>{this.state.errors["ip"]}</span>
                    </div>
                </div>     
                <div className="mb-3 row">
                    <label htmlFor="mask_cidr" className="col-sm-2 col-form-label">mask (CIDR)</label>
                    <div className="col-sm-10">
                        <input
                            className="form-control"
                            type="number"
                            name="mask_cidr"
                            id="mask_cidr"
                            value={mask_cidr || 32}
                            placeholder="32"
                            onChange={this.handleChange}
                            onBlur = {this.handleBlur} />
                            <span style={{display: "block"}}><small className="form-text text-muted"><i>default 32</i></small></span>
                            <span style={{color: "red"}}>{this.state.errors["mask_cidr"]}</span>
                    </div>
                </div>
                <div className="mb-3 row">
                <label htmlFor="next-hop" className="col-sm-2 col-form-label">next-hop</label>  
                    <div className="col-sm-10">
                        <input
                            className="form-control"
                            type="text"
                            name="next_hop"
                            id="next_hop"
                            value={next_hop || ''}
                            placeholder="0.0.0.0"
                            onChange={this.handleChange}
                            onBlur={this.handleBlur} />
                        <span style={{ display: "block" }}><small className="form-text text-muted"><i>next-hop (default 0.0.0.0)</i></small></span>
                        <span style={{ color: "red" }}>{this.state.errors["next_hop"]}</span>
                    </div>
                </div>        
                <input type="button" value="Submit" onClick={this.submitForm} disabled={!this.state.formValid} className="btn btn-outline-success" />                
            </form>            
        );
    }
}

export default Form;