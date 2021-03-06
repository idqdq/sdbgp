import React, { Component } from 'react'

class Form extends Component {
       
    initialState = {
        Data: {
            src: '',
            prefix_len: 32,
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
            if (this.state.Data.src && this.state.Data.next_hop) this.setState({ formValid: true });
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
            case 'src':
                if (value && !IpAddrPattern.test(value)) {
                    errors['src'] = 'must be a valid IP address'
                }
                break;          
            case 'prefix_len':                                
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
        const {src, prefix_len, next_hop } = this.state.Data;

        return (            
            <form>
                <div className="mb-3 row">
                    <label htmlFor="src" className="col-sm-2 col-form-label">ip</label>
                    <div className="col-sm-10">
                        <input
                            className="form-control"
                            type="text"
                            name="src"
                            id="src"
                            value={src || ''}
                            placeholder="1.2.3.4"
                            onChange={this.handleChange}
                            onBlur = {this.handleBlur} />
                            <span style={{display: "block"}}><small className="form-text text-muted"><i>IPv4 address</i></small></span>
                            <span style={{color: "red"}}>{this.state.errors["src"]}</span>
                    </div>
                </div>     
                <div className="mb-3 row">
                    <label htmlFor="prefix_len" className="col-sm-2 col-form-label">mask (CIDR)</label>
                    <div className="col-sm-10">
                        <input
                            className="form-control"
                            type="number"
                            name="prefix_len"
                            id="prefix_len"
                            value={prefix_len || 32}
                            placeholder="32"
                            onChange={this.handleChange}
                            onBlur = {this.handleBlur} />
                            <span style={{display: "block"}}><small className="form-text text-muted"><i>default 32</i></small></span>
                            <span style={{color: "red"}}>{this.state.errors["prefix_len"]}</span>
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