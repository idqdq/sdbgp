import Modal from "react-bootstrap/Modal";
import Form from './Form'
import FormBulk from './FormBulk'

const OneModal = (props) => {
    const modalTitle = props.index!==undefined && props.Data[props.index] ? 'Edit Prefix:' + props.Data[props.index].ip : 'New Prefix';
    return (
        <Modal show={props.isOpen}
            onHide={props.hideModal}
            backdrop="static"
            keyboard={false}
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
            keyboard={false}
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

export { OneModal, BulkModal, }
