import React, { Component } from 'react'

class FormBulk extends Component {

    constructor(props) {
        super(props);
        this.state = {
            Data: '', 
            next_hop: '0.0.0.0',
            errors: {},
            formValid: false,
        };  
    }
    
    handleAreaChange = (event) => {
        this.setState({ Data: event.target.value });
    }
    
    handleNHChange = (event) => {
        this.setState({ next_hop: event.target.value });
    }

    handleBlur = (event) => {
        const { name, value } = event.target
        
        if (this.validateField(name, value))
            if (this.state.errors[name]) {
                let newerrors = { ...this.state.errors };
                delete newerrors[name];
                this.setState({ errors: newerrors });
            }
            if (Object.keys(this.state.errors).length === 0) {
                this.setState({ formValid: true });
            }            
        else 
            this.setState({ formValid: false })
    }

    validateField(name, value) {
        const IpAddrPattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        
        const errors = {};        
        const lines = this.state.Data.split(/\r?\n/);

        if (name === 'area') {
            return (lines.every((line) => {                
                const res = line.trim().split('/');

                if (!res[0] || !IpAddrPattern.test(res[0])) {
                    errors[name] = 'content ' + res[0] + ' must be a valid IP addresses';
                    this.setState({ errors: {...this.state.errors, ...errors }});
                    return false;
                }                

                if (res[1]) {
                    const prefix_len = res[1].trim();
                    if (isNaN(prefix_len) || prefix_len > 32 || prefix_len < 16) {
                        errors[name] = 'prefix_len range 16..32';
                        this.setState({ errors: {...this.state.errors, ...errors }});
                        return false;
                    } 
                }                 
                return true;
            }))
        }             
        else if (name === 'next_hop') {
            if (value) {
                if (!IpAddrPattern.test(value)) {
                    errors[name] = 'must be a valid IP address';
                    this.setState({ errors: {...this.state.errors, ...errors }})
                    return false;
                }                
            }
            return true;
        }
    }
    
    submitForm = () => {
        const { Data, next_hop } = this.state;
        const data = [];
        const lines = Data.split(/\r?\n/);

        this.props.openSpinner();

        if (lines) {
            lines.every((line) => {
                const obj = {};
                const res = line.split('/');

                obj.src = res[0].trim();

                if (res[1])
                    obj.prefix_len = res[1];
                else
                    obj.prefix_len = 32;

                obj.next_hop = next_hop ? next_hop : '0.0.0.0';

                data.push(obj);
                return true;
            });
            
            this.props.handleSubmit(data);
        }
        this.props.hideSpinner();
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
                        <textarea 
                        name="area"
                        value={value} 
                        onChange={this.handleAreaChange} 
                        onBlur={this.handleBlur} 
                        style={taStyle}/>
                        <span style={{ color: "red" }}>{this.state.errors["area"]}</span>
                    </div>
                <label htmlFor="next-hop" className="col-sm-2 col-form-label">next-hop</label>  
                    <div className="col-sm-10">
                        <input
                            className="form-control"
                            type="text"
                            name="next_hop"
                            id="next_hop"
                            value={next_hop || ''}
                            placeholder="0.0.0.0"                            
                            onChange={this.handleNHChange}
                            onBlur={this.handleBlur} />
                        <span style={{ display: "block" }}><small className="form-text text-muted"><i>next-hop (default 0.0.0.0)</i></small></span>
                        <span style={{ color: "red" }}>{this.state.errors["next_hop"]}</span>
                    </div>
                <input type="button" value="Submit" onClick={this.submitForm} disabled={!this.state.formValid} className="btn btn-outline-success" /> 
            </form>
        )
    }
}

export default FormBulk;