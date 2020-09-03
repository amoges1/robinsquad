import React, {Fragment} from "react"

const Invested = ({purchases}) => {
    return (
        <Fragment>
            <div className="alert alert-success alert-dismissible ml-5 mr-5" role="alert">
                <button type="button" className="close" data-dismiss="alert">&times;</button>
                {
                    purchases.map(stock => 
                        <div key={stock.name}>
                            <h4 className="alert-heading">{stock.name}</h4>
                            <p className="mb-2">You've purchased {stock.quantity} shares/${stock.price} for a total of ${stock.total_price}!</p>
                        </div>
                    )
                }
            </div>
        </Fragment>
    )
}


export default Invested