import React, {Fragment} from "react"

const Navbar = () => {

    const handleLogout = async(e) => {
        e.preventDefault()
        try {
            const res = await fetch(`http://localhost:5000/logout?email=${localStorage.getItem("email")}`, {
                headers: {
                    'Access-Control-Allow-Origin':'*'
                }
            })
            const data = await res.json()
            if(data.msg === "Success logout") {
                window.location = "/"
                localStorage.clear()
            }
        } catch (err) {
            console.log(err)
        }
    }
    return (
        <Fragment>
            <div id="navigation">
                <nav className="navbar navbar-expand-sm bg-dark navbar-dark fixed-top">
                    <a className="navbar-brand" href="/account">
                        <img src={require("../img/logo.png")} alt="logo" style={{width:"2.55rem", borderRadius: ".5rem"}}/>
                    </a>
                    <a className="navbar-brand" href="/account">
                        <span><strong><span className="badge badge-warning">{localStorage.getItem("email")}</span> </strong> </span>
                    </a>
                    <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#collapsibleNavbar">
                        <span className="navbar-toggler-icon"></span>
                    </button>

                    <div className="collapse navbar-collapse justify-content-end" id="collapsibleNavbar">
                        <ul className="navbar-nav">
                            <li className="nav-item ">
                                <a className="nav-link" href="/" onClick={handleLogout}>Logout</a>
                            </li>
                        </ul>
                    </div>
                </nav>
            </div>
        </Fragment>
    )
}

export default Navbar