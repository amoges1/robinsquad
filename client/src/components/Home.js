import React, {Fragment} from "react"
import Navbar from "./Navbar"
import Portfolio from "./Portfolio"

const Home = () => {
    const footerStyling = {
        position: "fixed", 
        left: 0,
        bottom: 0, 
        width: "100%",
        backgroundColor:"#21ce99",
        color: "white",
        textAlign: "center"
        
    }
    if(!localStorage.getItem("email")) {
        return window.location = "/"
    } 
    return (
        <Fragment>
            <Navbar/>
            <Portfolio/>
            <footer style={footerStyling}><p style={{marginTop:"15px"}}>This is a personal project made for fun. All Respective icons and service(s) belong to Respective owners.</p>
            </footer>

        </Fragment>
    )
}

export default Home