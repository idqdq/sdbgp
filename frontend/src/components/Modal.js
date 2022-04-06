import { Modal } from "react-bootstrap";
import Form from './Form'
import FormBulk from './FormBulk'
import FlowspecForm from './FormFlowspec'
import '../spinner.css'

const OneModal = ({index, Data, ...props}) => {
    const modalTitle = index!==undefined && Data[index] ? 'Edit Prefix:' + Data[index].ip : 'New Prefix';
    return (
        <Modal show={props.isOpen}
            onHide={props.hideModal}
            backdrop="static"
        >
            <Modal.Header closeButton className="btn-success">
                <Modal.Title>{modalTitle}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Form handleSubmit={props.handleFormSubmit} Data={Data} changes={props.changes} index={index}/>
            </Modal.Body>
        </Modal>
    )
};

const BulkModal = (props) => {
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

const FlowspecModal = ({index, Data, ...props}) => {
    const modalTitle = index!==undefined && Data[index] ? 'Edit FlowSpec Policy:' + Data[index].src : 'New FlowSpec policy';
    return (
        <Modal show={props.isOpen}
            onHide={props.hideModal}
            backdrop="static"
        >
            <Modal.Header closeButton className="btn-success">
                <Modal.Title>{modalTitle}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <FlowspecForm handleSubmit={props.handleFormSubmit} Data={Data} changes={props.changes} index={index}/>
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

export { SpinerModal, OneModal, BulkModal, FlowspecModal }
