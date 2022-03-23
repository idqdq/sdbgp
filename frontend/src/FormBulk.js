import React, { Component } from 'react'

class FormBulk extends Component {

    constructor(props) {
        super(props);
        this.state = {
            Data: '', 
            next_hop: 'null',
            errors: {},
            formValid: true,
        };  
    }

    submitForm = () => {        
        const IpAddrPattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        const {Data, next_hop} = this.state;
        const errors = {};
        const data = [];        
        const lines = Data.split(/\r?\n/);
        
        lines.every((line) => {
            const obj = {};
            const res = line.split('/');

            const ip = res[0].trim();
            if(ip && IpAddrPattern.test(ip)){
                obj.ip = ip;
            } else {
                errors["ip"] = 'content ' + res[0] + ' must be a valid IP addresses';
                return false;
            }

            if (res[1]) {
                const mask_cidr = res[1].trim();
                if (isNaN(mask_cidr) || mask_cidr > 32 || mask_cidr < 16) {
                    errors["mask_cidr"] = 'content must be a valid IP addresses';
                    return false;
                } else {
                    obj.mask_cidr = mask_cidr;
                }
            } else
                obj.mask_cidr = 32;

            obj.next_hop = next_hop;
            data.push(obj);
            return true;   
        });

        if (Object.keys(errors).length) {
            this.setState({ errors: errors });
            this.setState({ formValid: false });            
        } else {
            this.setState({ errors: {} });
            this.setState({ formValid: true });
            this.props.handleSubmit(data);
        }              
    }
    
    handleAreaChange = (event) => {
        this.setState({ Data: event.target.value });
    }
    handleNHChange = (event) => {
        this.setState({ next_hop: event.target.value });
    }

    render() {        
        const { value, next_hop } = this.state;
        const taStyle = {
            height: '200px',
            width: '380px',
        }

        return (            
            <form>
                <label htmlFor="next-hop" className="col-sm-4 col-form-label">Список префиксов:</label> 
                    <div className="col-sm-10">
                        <textarea value={value} onChange={this.handleAreaChange} style={taStyle}/>
                        <span style={{ color: "red" }}>{this.state.errors["ip"]}</span>
                    </div>
                <label htmlFor="next-hop" className="col-sm-2 col-form-label">next-hop</label>  
                    <div className="col-sm-10">
                        <input
                            className="form-control"
                            type="text"
                            name="next_hop"
                            id="next_hop"
                            value={next_hop || ''}
                            placeholder="null"                            
                            onChange={this.handleNHChange}
                            onBlur={this.handleBlur} />
                        <span style={{ display: "block" }}><small className="form-text text-muted"><i>next-hop (default null)</i></small></span>
                        <span style={{ color: "red" }}>{this.state.errors["next_hop"]}</span>
                    </div>
                <input type="button" value="Submit" onClick={this.submitForm} disabled={!this.state.formValid} className="btn btn-outline-success" /> 
            </form>
        )
    }
}

export default FormBulk;