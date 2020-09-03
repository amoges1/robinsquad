import React, {Fragment, useState, useEffect} from "react"
import Stock from "./Stock"
import Main from "./Main"

const Portfolio = () => {
    const [portfolio, setPortfolio] = useState([])
    const [cash, setCash] = useState(0)
    const [equity, setEquity] = useState(0)
    
    const getPortfolio = async() => {
        try {
            const res = await fetch(`http://localhost:5000/account?email=${localStorage.getItem("email")}`, {
                headers: {
                    'Access-Control-Allow-Origin':'*'
                  }
            })
            const data = await res.json()
            console.log(data);
            setPortfolio(data.portfolio)
            setCash(data.cash)
            setEquity(data.equity)

        } catch (err) {
            console.log(err)
        }
    }

    useEffect( () => {
        getPortfolio()
    }, [])

    return (
        <Fragment>
            <div id="positions" className="container-fluid">
                {
                    cash !== 0 ? (
                        <Main cash={cash} equity={equity}/>
                    ) : null
                }
                <ul>
                { 
                    portfolio.length === 0 ? (
                        <Fragment>
                        <div className="progress">
                            <div className="progress-bar bg-success progress-bar-striped progress-bar-animated" role="progressbar"     aria-valuenow="75"    aria-valuemin="0"    aria-valuemax="100" style={{ width: "75%" }}>
                            Loading...
                            </div>
                        </div>
                    </Fragment>
                    ) : ( 
                        Object.keys(portfolio).map(el => <Stock ticker={el} info={portfolio[el]} key={el}/>)   
                    )
                } 
                </ul>
            </div> 
        </Fragment>
    )
}

export default Portfolio
