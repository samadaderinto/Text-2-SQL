import { ReactElement, useState } from "react";
import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch, IoPeopleOutline, IoSettingsOutline } from "react-icons/io5";
import { PiDiamondsFourFill } from "react-icons/pi";
import { RiSpeakLine, RiShoppingBag3Line } from "react-icons/ri";
import {  RxDashboard } from 'react-icons/rx'
import { MdOutlineShoppingCart } from "react-icons/md";
import { Outlet } from "react-router-dom";
import { Dashboard } from "../Components/Dashboard";
import { Product } from "../Components/Product";
import { Orders } from "../Components/Orders";
import { Customers } from "../Components/Customers";
import { Settings } from "../Components/Settings";

const Home = () => {

  const [activeIndex, setActiveIndex] = useState< number | null>(null)
  const [active, setActive] = useState('')

  interface item {
    icon: ReactElement,
    itemName: string
  }

  const sideBarArrayList: item[] = [
    {
      icon: <RxDashboard/>,
      itemName: 'Dashboard'
    },
    {
      icon: <RiShoppingBag3Line/>,
      itemName: 'Products'
    },
    {
      icon: <MdOutlineShoppingCart/>,
      itemName: 'Orders'
    },
    {
      icon:<IoPeopleOutline/>,
      itemName: 'Customers'
    },
    {
      icon: <IoSettingsOutline/>,
      itemName: 'Settings'
    },
  ]

  return (
    <div className="Home_Container">
      <div className='Header_Container'>
        <span><PiDiamondsFourFill /> EchoCart</span>
        <section className="Search_Container">
          <p><IoSearch /></p>
          <input type="text" placeholder="Search anything..." />
          <p><RiSpeakLine /></p>
        </section>
        <section className="RightHand_Container">
          <p className="Exclusive_Store">Exclusive Store</p>
          <p><IoIosNotificationsOutline /></p>
          <div className="Image_Container">

          </div>
        </section>

      </div>
     <div className="Main_Container">
     <nav className="Home_Sidebar">
        <div className="Sidebar_Container">

          {
            sideBarArrayList.map((obj, index)=> (
              <span 
              key={index}
              onClick={()=> { 
                setActive(obj.itemName)              
                setActiveIndex(index)}} 
              className={activeIndex === index? 'Active_List': ''}>
              <p className="List_icon">{obj.icon}</p>
              <p>{obj.itemName}</p>
            </span>
            ))

            
          }

        </div>
      </nav>
      <section className="Home_Content__Container">
        {
          active === 'Dashboard'? <Dashboard/>:
          active === 'Products'? <Product/>:
          active === 'Orders'? <Orders/>:
          active === 'Customers'? <Customers/>:
          active === 'Settings'? <Settings    />: null

        }
      </section>
     </div>
      <Outlet />



    </div>
  )
}

export default Home;