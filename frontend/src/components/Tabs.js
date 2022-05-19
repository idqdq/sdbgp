import { Tabs, Tab } from "react-bootstrap";
import Container from "react-bootstrap/Container";

const AppTabs = ({activeKey, onSelect, isAdmin}) => {    
    return (
      <Tabs
        id="controlled-tab-example"
        activeKey={activeKey}
        onSelect={onSelect}
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
                <h4>BGP FlowSpec</h4>
              </div>
          </Container>
        </Tab>
        
        {isAdmin && <Tab eventKey="logging" title="Logg" >
          <Container />                        
        </Tab>}

        {isAdmin && <Tab eventKey="admin" title="Admin" >
          <Container>
          </Container>
        </Tab>}

        <Tab eventKey="help" title="Help" >
          <Container>
          </Container>
        </Tab>
      </Tabs>
    );
  }

export default AppTabs