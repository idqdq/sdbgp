import { removeToken } from '../helpers';


export default function Admin(){

    const handleSubmit = async e => {
        e.preventDefault();        
        removeToken();  
        window.location.reload();   
    }    

    return (
        <div>
            <input type="button" value="LogOut" onClick={handleSubmit} className="btn btn-outline-success" />
        </div>
    )
}