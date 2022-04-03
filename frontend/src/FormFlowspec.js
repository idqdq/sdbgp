import { Component } from 'react'
import { Form, Button } from "react-bootstrap";

class FlowspecForm extends Component {       
    initialState = {
        Data: {
            ip: '',
            prefix_len: 32,
            next_hop: '',  
            src: '',
            src_prefix_len: 32,
            dst: '',
            dst_prefix_len: 32,
            src_ports: '',
            dst_ports: '',
            protocols: [],
            rate_limit: 0,          
        },
        errors: {},
        formValid: false,
    }


    render() {
        return (<Form>
            <Form.Group className="mb-3" controlId="formBasicEmail">
              <Form.Label>Email address</Form.Label>
              <Form.Control type="email" placeholder="Enter email" />
              <Form.Text className="text-muted">
                We'll never share your email with anyone else.
              </Form.Text>
            </Form.Group>
          
            <Form.Group className="mb-3" controlId="formBasicPassword">
              <Form.Label>Password</Form.Label>
              <Form.Control type="password" placeholder="Password" />
            </Form.Group>
            <Form.Group className="mb-3" controlId="formBasicCheckbox">
              <Form.Check type="checkbox" label="Check me out" />
            </Form.Group>
            <Button variant="primary" type="submit">
              Submit
            </Button>
          </Form>)
    }
}

export default FlowspecForm