import React, {Fragment} from "react"

//stock is object = {ticker + info} from <Stock/>
const Stock = (stock) => {
    const { name, quantity, equity, percentage} = stock.info
    return (
        <Fragment>
            <li className="list-group-item bg-dark rounded" >
            <div>
              <h6 className="text-center text-white border-white">
                {name}
              </h6>
            </div>
            <div className="text-center">
              <span className="badge badge-pill badge-warning badge-positions">
                {" "}
                <strong> {stock.ticker}</strong>{" "}
              </span>
              <span className="badge badge-pill badge-info badge-positions">
                {" "}
                <strong>{Math.round(quantity,2)} shares</strong>
              </span>
              <span className="badge badge-pill badge-primary badge-positions">
                <strong>${equity}</strong>
              </span>
              <span className="badge badge-pill badge-success badge-positions">
                {" "}
                <strong> {percentage}%</strong>
              </span>
            </div>
          </li>
        </Fragment>
    )
}

export default Stock