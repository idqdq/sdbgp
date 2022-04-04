import { Modal } from "react-bootstrap";
import Form from './Form'
import FormBulk from './FormBulk'
import FlowspecForm from './FormFlowspec'
import './spinner.css'

const OneModal = (props) => {
    const modalTitle = props.index!==undefined && props.Data[props.index] ? 'Edit Prefix:' + props.Data[props.index].ip : 'New Prefix';
    return (
        <Modal show={props.isOpen}
            onHide={props.hideModal}
            backdrop="static"
        >
            <Modal.Header closeButton className="btn-success">
                <Modal.Title>{modalTitle}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Form handleSubmit={props.handleFormSubmit} Data={props.Data} changes={props.changes} index={props.index}/>
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

const FlowspecModal = (props) => {
    const modalTitle = props.index!==undefined && props.Data[props.index] ? 'Edit FlowSpec Policy:' + props.Data[props.index].src : 'New FlowSpec policy';
    return (
        <Modal show={props.isOpen}
            onHide={props.hideModal}
            backdrop="static"
        >
            <Modal.Header closeButton className="btn-success">
                <Modal.Title>{modalTitle}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <FlowspecForm handleSubmit={props.handleFormSubmit} Data={props.Data} changes={props.changes} index={props.index}/>
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
