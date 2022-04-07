import { Modal } from "react-bootstrap";
import Form from './Form'
import FormBulk from './FormBulk'
import FlowspecForm from './FormFlowspec'
import '../spinner.css'

const Entity = {
    unicast: 'Prefix',
    flowspec: 'FlowSpec Policy',
}

const FormModal = ({Tab, Data, index, ...props}) => {
    const modalTitle = index!==undefined && Data[index] ? 'Edit ' + Entity[Tab] + ': ' + Data[index].src : 'New ' + Entity[Tab];
    return (
        <Modal show={props.isOpen}
            onHide={props.hideModal}
            backdrop="static"
        >
            <Modal.Header closeButton className="btn-success">
                <Modal.Title>{modalTitle}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                { Tab==='unicast' && <Form handleSubmit={props.handleFormSubmit} Data={Data} changes={props.changes} index={index}/>}
                { Tab==='flowspec' && <FlowspecForm handleSubmit={props.handleFormSubmit} Data={Data} changes={props.changes} index={index}/>}
            </Modal.Body>
        </Modal>
    )
};

const FormBulkModal = (props) => {
    const modalTitle = 'Bulk Prefix loads';
    return (
        <Modal show={props.isOpen}
            onHide={props.hideModal}
            backdrop="static"
        >
            <Modal.Header closeButton className="btn-success">
                <Modal.Title>{modalTitle}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <FormBulk handleSubmit={props.handleFormSubmit} />
            </Modal.Body>
        </Modal>
    )
};


const SpinerModal = (props) => {
    if (props.show)
        return (
            <div className="modal-spinner">
                <div id="blabla" className="spinner"></div>
            </div>
        )
    else return null;
}

export { SpinerModal, FormModal, FormBulkModal }
