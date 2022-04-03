import { Tabs, Tab } from "react-bootstrap";
import Container from "react-bootstrap/Container";

const AppTabs = (props) => {
    
    return (
      <Tabs
        id="controlled-tab-example"
        activeKey={props.activeKey}
        onSelect={props.onSelect}
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