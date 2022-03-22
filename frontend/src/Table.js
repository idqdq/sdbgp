import React from 'react'

const TableHeader = () => {
    return (
        <thead>
            <tr>
                <th>prefix</th>
                <th>mask</th>
                <th>next-hop</th>                
            </tr>
        </thead>
    )
}

const buttonStyle = {
    margin: '0px 5px',
}

const TableBody = (props) => {    
    const rows = props.Data.map((row, index) => {
        return (
            <tr key={index}>
                <td>{row.ip}</td>
                <td>{row.mask_cidr}</td>
                <td>{row.next_hop}</td>                
                <td>
                    <button onClick={() => props.pxEdit(index)} disabled={props.changes[row.ip]==="new"} style={buttonStyle} className="btn btn-outline-primary btn-sm">Edit</button>
                    <button onClick={() => props.pxRemove(index)} style={buttonStyle} className="btn btn-outline-danger btn-sm">Delete</button>
                </td>
            </tr>

        )
    })

    return <tbody>{rows}</tbody>
}

const Table = (props) => {
    const { Data, changes, pxEdit, pxRemove } = props

    return (
        <table className="table table-hover">
            <TableHeader />
            <TableBody Data={Data} changes={changes} pxEdit={pxEdit} pxRemove={pxRemove}  />
        </table>
    )
}

export default Table