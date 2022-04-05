import { Component } from 'react'
import { Form, Button, ToggleButton, ToggleButtonGroup } from "react-bootstrap";

const ACTION_DISCARD = '1';
const ACTION_ACCEPT = '2';
const ACTION_RATE_LIMIT = '3';

class FlowspecForm extends Component {       
    initialState = {
        Data: {            
            src: '',            
            dst: '',            
            src_ports: '',
            dst_ports: '',
            protocols: '',
            action: ACTION_DISCARD,
            rate_limit: 0,          
        },
        chckbx: false,
        errors: {},
        formValid: false,
    }

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

    handleClickChkBx = () => { 
        this.setState( prev => ({ chckbx: !prev.chckbx }));        
    }

    handleBlur = (event) => {
        const { name, value } = event.target
        
        this.validateField(name, value);
        this.isFormValid();        
    }

    handleAction = (e) => {
        e.preventDefault();        
        this.setState ({ 
            Data: { ...this.state.Data, action: e.target.previousSibling.value } //magic
        })        
    }

    isFormValid = () => {
      if (Object.keys(this.state.errors).length === 0) {
          if (this.state.Data.src) this.setState({ formValid: true });
      }
    }

    validateField(name, val){        
      const errors = {};                
      const regex_ipv4 = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
      const regex_ipv4prefix = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\/(3[0-2]|[1-2][0-9]|[0-9])$)/;
      const portRangePattern = /^(\d+[,-]*)+\d$/;
      const protocolsPattern = /^([A-Za-z]+,\s?)*[A-Za-z]+$/;
      const protomap = ['tcp', 'udp', 'icmp', 'gre', 'esp'];
      const value = val.trim();

      switch(name) {        
          case 'src':
          case 'dst':
              if (value && !regex_ipv4.test(value) && !regex_ipv4prefix.test(value)) {
                  errors[name] = 'must be a valid IP address'
              }
              break;          
          case 'src_ports':    
          case 'dst_ports':                            
              if(value && !portRangePattern.test(value)) {
                  errors[name] = 'must be numbers separated by comma (,) or dash (-)';                    
              }                        
              break;
          case 'protocols':
              if (value) {
                  if (!protocolsPattern.test(value)) {
                      errors[name] = 'must be comma separated words'
                  }
                  else {                    
                    value.split(',').forEach((x)=>{if (protomap.indexOf(x)===-1) errors[name] = x + ' is not a valid protocol'});
                  }
              }
              break;
          case 'rate_limit':
              if (value && isNaN(value)) {
                 errors[name] = 'rate-limit must be a number {0..1000000000}';
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
    const { chckbx } = this.state;
    const action = this.state.Data.action;

    return (<>
      <Form>
        <Form.Group className="mb-3" controlId="formFlowSRC">
          <Form.Label>src prefix (mandatory field)</Form.Label>
          <Form.Control
            name="src" type="text" placeholder="1.1.1.1/32"
            onChange={this.handleChange}
            onBlur={this.handleBlur}
            className={this.state.errors["src"] ? "is-invalid" : ""}
          />
          <span style={{ color: "red", display: "block" }}>{this.state.errors["src"]}</span>
          <Form.Text className="text-muted" >
            default prefix len is 32
          </Form.Text>          
        </Form.Group>
        <Form.Group className="mb-3" controlId="formFlowDST">
          <Form.Label>dst prefix</Form.Label>
          <Form.Control
            name="dst" type="text" placeholder="2.2.2.2/32"
            onChange={this.handleChange}
            onBlur={this.handleBlur}
            className={this.state.errors["dst"] ? "is-invalid" : ""}
          />
          <span style={{ color: "red", display: "block" }}>{this.state.errors["dst"]}</span>
          <Form.Text className="text-muted">
            default prefix len is 32
          </Form.Text>
        </Form.Group>
        <Form.Group className="mb-3" controlId="formFlowCheckbox">
          <Form.Check type="checkbox" checked={chckbx} label="Advanced attributes" onChange={this.handleClickChkBx} />
        </Form.Group>
        {/* Advanved attributes */}
        {chckbx && <>
          <Form.Group className="mb-3" controlId="formFlowSRCPorts">
            <Form.Label>src ports</Form.Label>
            <Form.Control
              name="src_ports" type="text" placeholder="3000, 4000, 8080-8088"
              onChange={this.handleChange}
              onBlur={this.handleBlur}
              className={this.state.errors["src_ports"] ? "is-invalid" : ""}
            />
            <span style={{ color: "red", display: "block" }}>{this.state.errors["src_ports"]}</span>
            <Form.Text className="text-muted">
              comma separated numbers and ranges
            </Form.Text>
          </Form.Group>
          <Form.Group className="mb-3" controlId="formFlowDSTPorts">
            <Form.Label>dst ports</Form.Label>
            <Form.Control
              name="dst_ports" type="text" placeholder="80,443,8080-8088"
              onChange={this.handleChange}
              onBlur={this.handleBlur}
              className={this.state.errors["dst_ports"] ? "is-invalid" : ""}
            />
            <span style={{ color: "red", display: "block" }}>{this.state.errors["dst_ports"]}</span>
            <Form.Text className="text-muted">
              comma separated numbers and ranges
            </Form.Text>
          </Form.Group>
          <Form.Group className="mb-3" controlId="formFlowProto">
            <Form.Label>protocols</Form.Label>
            <Form.Control
              name="protocols" type="text" placeholder="tcp,udp"
              onChange={this.handleChange}
              onBlur={this.handleBlur}
              className={this.state.errors["protocols"] ? "is-invalid" : ""}
            />
            <span style={{ color: "red", display: "block" }}>{this.state.errors["protocols"]}</span>
            <Form.Text className="text-muted">
              IP protocols (comma separated): tcp, udp, icmp, gre, esp
            </Form.Text>
          </Form.Group>
        </>}
        <Form.Label>Action:</Form.Label>
        <div className="input-group mb-4">
          <ToggleButtonGroup
            name="action"
            value={action}
            onClick={this.handleAction}>
            <ToggleButton name="action" value={ACTION_DISCARD} variant="outline-danger">discard</ToggleButton>
            <ToggleButton name="action" value={ACTION_ACCEPT} variant="outline-danger">accept</ToggleButton>
            <ToggleButton name="action" value={ACTION_RATE_LIMIT} variant="outline-danger">rate-limit (Bps)</ToggleButton>
          </ToggleButtonGroup>
          <Form.Control type="text"
            name="rate_limit"
            placeholder="100000"
            disabled={action !== ACTION_RATE_LIMIT}
            onChange={this.handleChange}
            onBlur={this.handleBlur}
            className={this.state.errors["rate_limit"] ? "is-invalid" : ""}
          />
          <span style={{ color: "red", display: "block" }}>{this.state.errors["rate_limit"]}</span>
        </div>
        <input type="button" value="Submit" onClick={this.submitForm} disabled={!this.state.formValid} className="btn btn-outline-success" />
      </Form>
    </>)
  }
}

export default FlowspecForm