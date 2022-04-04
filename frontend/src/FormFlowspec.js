import { Component } from 'react'
import { Form, Button, ToggleButton } from "react-bootstrap";

const ACTION_DISCARD = '1';
const ACTION_ACCEPT = '2';
const ACTION_RATE_LIMIT = '3';

class FlowspecForm extends Component {       
    initialState = {
        Data: {            
            src: '',
            src_prefix_len: 32,
            dst: '',
            dst_prefix_len: 32,
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

    handleAction = (event) => {
        alert(this.state.action)
        this.setState ({ 
            Data: { ...this.state.Data, action: event.target.value }
        })
    }

  render() {
    const { chckbx, action } = this.state;

    return (<>
      <Form>
        <Form.Group className="mb-3" controlId="formFlowSRC">
          <Form.Label>src prefix (mandatory field)</Form.Label>
          <Form.Control name="src" type="text" placeholder="1.1.1.1/32" onChange={this.handleChange} />
          <Form.Text className="text-muted">
            default prefix len is 32
          </Form.Text>
        </Form.Group>
        <Form.Group className="mb-3" controlId="formFlowDST">
          <Form.Label>dst prefix</Form.Label>
          <Form.Control name="dst" type="text" placeholder="2.2.2.2/32" onChange={this.handleChange} />
          <Form.Text className="text-muted">
            default prefix len is 32
          </Form.Text>
        </Form.Group>
        <Form.Group className="mb-3" controlId="formFlowCheckbox">
          <Form.Check type="checkbox" checked={chckbx} label="Advanced attributes" onChange={this.handleClickChkBx}   />
        </Form.Group>
        {chckbx && <fieldset>
          <Form.Group className="mb-3" controlId="formFlowSRCPorts">
            <Form.Label>src ports</Form.Label>
            <Form.Control name="src_ports" type="text" placeholder="3000, 4000, 8080-8088" onChange={this.handleChange} />
            <Form.Text className="text-muted">
              comma separated numbers and ranges
            </Form.Text>
          </Form.Group>
          <Form.Group className="mb-3" controlId="formFlowDSTPorts">
            <Form.Label>dst ports</Form.Label>
            <Form.Control name="dst_ports" type="text" placeholder="80,443,8080-8088" onChange={this.handleChange} />
            <Form.Text className="text-muted">
              comma separated numbers and ranges
            </Form.Text>
          </Form.Group>
          <Form.Group className="mb-3" controlId="formFlowProto">
            <Form.Label>protocols</Form.Label>
            <Form.Control name="protocols" type="text" placeholder="tcp,udp" />
            <Form.Text className="text-muted">
              comma separated IP protocols. tcp and udp might have ports
            </Form.Text>
          </Form.Group>
        </fieldset>}
        <Form.Group className="mb-4" controlId="formFlowAction">
          <Form.Label>Action</Form.Label><br></br>
          <div className="input-group mb-4">          
          <ToggleButton name="action" type="radio" variant="outline-danger" value={ACTION_DISCARD}
            checked={action===ACTION_DISCARD} onChange={this.handleAction} >
            discard
          </ToggleButton>
          <ToggleButton name="action" type="radio" variant="outline-danger" value={ACTION_ACCEPT}
            checked={action===ACTION_ACCEPT} onChange={this.handleAction}>
            accept
          </ToggleButton>
          <ToggleButton name="action" type="radio" variant="outline-danger" value={ACTION_RATE_LIMIT}
            checked={action===ACTION_RATE_LIMIT} onClick={this.handleAction}>
            rate-limit
          </ToggleButton>          
          <Form.Control type="text"
            className=""
            placeholder="0"
            disabled={action !== ACTION_RATE_LIMIT} />
          </div>
        </Form.Group>

        <Button variant="primary" type="submit">
          Submit
        </Button>
      </Form>
    </>)
  }
}

export default FlowspecForm