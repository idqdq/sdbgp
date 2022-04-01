import { Tabs, Tab } from "react-bootstrap";
import Container from "react-bootstrap/Container";
import { useState } from 'react';

const AppTabs = (props) => {
    const [key, setKey] = useState('unicast');
  
    return (
      <Tabs
        id="controlled-tab-example"
        activeKey={key}
        onSelect={(k) => setKey(k)}
        className="mb-3"
      >
        <Tab eventKey="unicast" title="BGP Unicast">
          <Container>
              <div>
              <h4>BGP Unicast</h4>
              </div>
          </Container>
        </Tab>
        <Tab eventKey="flowspec" title="BGP FlowSpec">
          <Container>
              <div>
                <h4>BGP FlowSpec (to be implemented)</h4>
              </div>
          </Container>
        </Tab>
        <Tab eventKey="help" title="Help" disabled>
          <Container>
          </Container>
        </Tab>
      </Tabs>
    );
  }

export default AppTabs