import React from 'react'


const tabHeaders = {
    unicast: ['ip', 'prefix_len', 'next_hop'],
    flowspec: ['src', 'dst', 'src_ports', 'dst_ports', 'protocols', 'action', 'rate_limit'],
}

const ACTION_MAP = {
    1: 'discard',
    2: 'accept',
    3: 'rate-limit',
}

const TableHeader = ({ Tab }) => {
    const header = tabHeaders[Tab].map((value, index) => {
        return (<th key={index}>{value}</th>)
    })

    return <thead><tr>{header}</tr></thead>
}

const buttonStyle = {
    margin: '0px 5px',
}

const TableBody = ({Data, ...props}) => {
    const rows = Data.map((row, index) => {
        return (
            <tr key={index}>{
                Object.values(row).map((value, x) => {
                    if (x===5) return (<td key={x}>{ACTION_MAP[value]}</td>);
                    return (<td key={x}>{value}</td>)
                })}
                <td>
                    <button onClick={() => props.pxEdit(index)} disabled={props.changes[row.src] === "new"} style={buttonStyle} className="btn btn-outline-primary btn-sm">Edit</button>
                    <button onClick={() => props.pxRemove(index)} style={buttonStyle} className="btn btn-outline-danger btn-sm">Delete</button>
                </td>
            </tr>
        )
    })

    return <tbody>{rows}</tbody>
}

const Table = ({ Tab, Data, changes, pxEdit, pxRemove }) => {    
    return (
        <table className="table table-hover">
            <TableHeader Tab={Tab} />
            <TableBody Data={Data} changes={changes} pxEdit={pxEdit} pxRemove={pxRemove}  />
        </table>
    )
}

export default Table