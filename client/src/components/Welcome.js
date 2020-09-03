import React, {Fragment, useState} from "react"

const Welcome = () => {

    const [email, setEmail] = useState("Email address")
    const [password, setPassword] = useState("Password")
    

    const containerStyling = {
        paddingTop:"60px",
        paddingBottom:"60px"
    }
    const formStyling = {
        width: "100%",
        maxWidth: "330px",
        padding: "15px",
        margin: "auto",
        textAlign: "center"
    }

    const loginButtonStyling = {
        background: "#21ce99"
    }

    const imgStyling = {
        height:"50%",
        width:"inherit"
    }
    const handleForm = async(e) => {
        e.preventDefault()
        try {
            let formData = new FormData()
            formData.append("email", email)
            formData.append("password", password)
            const res = await fetch("http://localhost:5000/home", {
                method: "POST",
                body: formData,
                headers: {
                    'Access-Control-Allow-Origin':'*'
                  }
            }) // TEST THIS HERE NEXT! Run flask (API) + react (frontend) 
            const data = await res.json()
            if(data.msg === "Signed in") {
                localStorage.setItem("email", email)
                localStorage.setItem("password", password)
                window.location = "/account"
            }

        } catch (err) {
            console.log(err)
        }
    }

    return (
        <Fragment>
            <div className="container" style={containerStyling}>
                <form className="form" style={formStyling} onSubmit={handleForm}>
                    <img className="mb-4 img-responsive" src={require("../img/logo.png")} alt="robinhood_logo" style={imgStyling} />

                    <h1 className="h3 mb-3 font-weight-400">Let's get this money!</h1>
                    <label htmlFor="inputEmail" className="sr-only">Email address</label>
                    <input type="email" className="form-control"  placeholder="Email address" onChange={e => setEmail(e.target.value)} required autoFocus />
                    <br />
                    <label htmlFor="inputPassword" className="sr-only">Password</label>
                    <input type="password" className="form-control" placeholder="Password" onChange={e => setPassword(e.target.value)} required />
                    <br />
                    <button type="submit" className="btn btn-lg btn-primary btn-block" style={loginButtonStyling} >Log in </button>
                    <p className="mt-5 mb-3 text-muted">This is a personal project made for fun. All Respective icons and service(s) belong to Respective owners.</p>
                </form>
            </div>
        </Fragment>
       
    
    )
}

export default Welcome