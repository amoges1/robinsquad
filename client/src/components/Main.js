import React, {Fragment, useState} from "react"
import Invested from "./Invested"

const Main = ({cash, equity}) => {
    const [maxAmt, setMaxAmt] = useState(3)
    const [purchases, setPurchases] = useState([])
    // set Alert to show results from handleInvest!
    const handleInvest = async(e) => {
        e.preventDefault()
        try {
            const res = await fetch(`http://localhost:5000/invest?email=${localStorage.getItem("email")}&password=${localStorage.getItem("password")}&max_amt=${maxAmt}`, {
                method: "GET",
                headers: {
                    'Access-Control-Allow-Origin':'*'
                  }
            })       
            const data = await res.json()
            setPurchases(data)            
        } catch (err) {
            console.log(err);
        }
    }
    return (
        <Fragment>
            <ul className="list-line text-center pt-3">
        <li className="list-group-item bg-dark rounded">
          <div>
            <h6 className="text-center text-white border-white"> Balance: </h6>
          </div>
          <div className="text-center">
            <h4>
              <span className="badge badge-pill badge-success badge-positions">
                ${Math.round(equity, 2)}{" "}
              </span>
            </h4>
          </div>
        </li>
        <li className="list-group-item bg-dark rounded">
          <div>
            <h6 className="text-center text-white border-white"> Cash: </h6>
          </div>
          <div className="text-center">
            <h4>
              <span className="badge badge-pill badge-success badge-positions">
                ${cash}{" "}
              </span>
            </h4>
          </div>
        </li>
        <li className="list-group-item bg-dark rounded">
          <div className="mt-1">
            <h6 className="text-center text-white border-white"> Auto:  </h6>
          </div>
          <div className="text-center">
            <h4>
                <form onSubmit={handleInvest}>
                    <div className="input-group input-group-sm">
                        <input type="text" className="form-control" size="2" placeholder={maxAmt} onChange={(e) => setMaxAmt(e.target.value)}data-toggle="tooltip" title="Set limit of each stock purchase"/>
                        <div className="input-group-append">
                            <button className="btn btn-success" type="submit" data-toggle="tooltip"
                    title="Click me to auto invest your money &#9889;">Invest</button>
                        </div>
                    </div>
                </form>

            </h4>
          </div>
        </li>
      </ul>
      {
          purchases.length === 0 ? null : <Invested purchases={purchases}/>
      }
        </Fragment>
    )
}

export default Main