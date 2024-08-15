// import  {   useState } from "react";

import { Outlet } from "react-router-dom";
// import { Dashboard } from "../Components/Dashboard";
// import { Product } from "../Components/Product";
// import { Orders } from "../Components/Orders";
// import { Customers } from "../Components/Customers";
// import { Settings } from "../Components/Settings";
// import PageNotFound from "./PageNotFound";
// import axios from "axios";
// import { Logout } from "../Components/Logout";

const Home = () => {

 




  // setActive('Dashboard')

  return (
    <div className="Home_Container">

     <div className="Main_Container"> 
     
      <section className="Home_Content__Container">
        {
          // active === 'Dashboard'? <Dashboard/>:
          // active === 'Products'? <Product/>:
          // active === 'Orders'? <Orders/>:
          // active === 'Customers'? <Customers/>:
          // active === 'Settings'? <Settings />: 
          // active === 'Logout'?:
          // active === '*'? <PageNotFound/>: null

          }
        </section>
      </div>
      <Outlet />



    </div>
  )
}

export default Home;