class Positions extends React.Component {
    
    state = {
        account: null
    }

    componentDidMount() {
        fetch("http://127.0.0.1:5000/account")
        .then(res => res.json()) //parse as json 1st level
        .then(data => this.setState({account: data }))
                
    }

    render() {

        if(!this.state.account) {
            return (
                <div className="progress">
                    <div className="progress-bar bg-success progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100" style={{width: "75%"}}></div>
                </div>
            )
        } else {
            let stocks = [];
            
            this.state.account.positions.forEach( (stock, index) => {
                // convert String text 'dict' into JSON Object, 2nd level
                let stockObj = JSON.parse(stock)
                stocks.push(<li className="list-group-item bg-dark rounded" key={index}>
                            <div>
                                <h6 className="text-center text-white border-white"> { stockObj.name }</h6>
                            </div>
                            <div className="text-center">                                
                                <span className="badge badge-pill badge-warning badge-positions"> <strong> {stockObj.symbol}</strong> </span>
                                <span className="badge badge-pill badge-info badge-positions"> <strong>{Math.round(stockObj.quantity)} shares</strong></span>
                                <span className="badge badge-pill badge-primary badge-positions"><strong>${Math.round(stockObj.total_value * 100)/100}</strong></span>
                                <span className="badge badge-pill badge-success badge-positions"> <strong> {Math.round(stockObj.percentage * 1000)/1000}%</strong></span>
                            </div>
                        </li>)
            });

            return( 
                <div>
                    <ul className="list-line text-center pt-3">
                        <li className="list-group-item bg-dark rounded">
                            <div>
                                <h6 className="text-center text-white border-white"> Balance: </h6>
                            </div>
                            <div className="text-center">                                
                                <h4><span className="badge badge-pill badge-success badge-positions"> 
                                ${ Math.round(this.state.account.equity * 100)/100 } </span>
                                </h4>
                            </div>
                        </li>
                        <li className="list-group-item bg-dark rounded">
                            <div>
                                <h6 className="text-center text-white border-white"> Cash: </h6>
                            </div>
                            <div className="text-center">                                
                                <h4><span className="badge badge-pill badge-success badge-positions"> 
                                ${ Math.round(this.state.account.avail_cash * 100)/100 } </span>
                                </h4>
                            </div>
                        </li>
                        <li className="list-group-item bg-dark rounded">
                            <div>
                                <h6 className="text-center text-white border-white"> Auto: </h6>
                            </div>
                            <div className="text-center">                                
                                <h4> <a className="badge badge-pill badge-success badge-positions" 
                                    href="/invest" data-toggle="tooltip" title="Click me to auto invest your money &#9889;"> Invest</a>
                                </h4>
                            </div>
                        </li>
                    </ul>
                    <section className="positions-title">
                        <p className="display-4 text-center">Positions</p>
                    </section>
                    <ul className="list-line text-center pb-5">
                    {
                        stocks
                    } 
                    </ul>
                </div>
                
            )
        }
      
    }   
}

ReactDOM.render(<Positions />, document.getElementById("positions"));
