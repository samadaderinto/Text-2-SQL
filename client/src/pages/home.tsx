// import  {   useState } from "react";

import { Outlet } from "react-router-dom";
// import { Dashboard } from "../Components/Dashboard";
// import { Product } from "../Components/Product";
// import { Orders } from "../Components/Orders";
// import { Customers } from "../Components/Customers";
// import { Settings } from "../Components/Settings";
// import { PageNotFound } from "./PageNotFound";
// import axios from "axios";
// import { API_BASE_URL } from "../utils/api"
// import { RiLogoutBoxLine, RiShoppingBag3Line } from "react-icons/ri";
// import { RxDashboard } from "react-icons/rx";
// import { IoPeopleOutline, IoSettingsOutline } from "react-icons/io5";
// import { MdOutlineShoppingCart } from "react-icons/md";
// import { Logout } from "../Components/Logout";

const Home = () => {

 




  // setActive('Dashboard')

  return (
    <div className="Home_Container">

     <div className="Main_Container"> 
     
      <section className="Home_Content__Container">
        
        </section>
      </div>
      <Outlet />



    </div>
  )
}

export default Home;