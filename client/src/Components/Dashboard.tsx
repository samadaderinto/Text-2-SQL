import { useState  } from "react";
import {  HiOutlineChartSquareBar } from 'react-icons/hi'
import {  RiShoppingBag4Line } from 'react-icons/ri'
import { GoContainer } from "react-icons/go";
import {  IoPeopleOutline  } from 'react-icons/io5'
import LaptopImg from '../assets/editing-laptop-2048px-231551-2x1-1.webp'

import { DashboardCardProps } from "../types/dashboard";
import SideBar from "../layouts/SideBar";
import { Header } from "../layouts/Header"

export const Dashboard = () => {

  const  [Active, setActive] = useState< number | null>(null)



const cardArray: DashboardCardProps[] = [

  {
    icon: <HiOutlineChartSquareBar/>,
    title: 'Total Sales',
    value: 271568.09,
    percent: 25.5,
    increment: 15
  },
{
  icon: <RiShoppingBag4Line/>,
  title: 'Total Sale',
  value: 271568.09,
  percent: 25.5,
  increment: 15
},
{
  icon: <GoContainer/>,
  title: 'Total Sales',
  value: 271568.09,
  percent: 25.5,
  increment: 15
},
{
  icon: <IoPeopleOutline/>,
  title: 'Total Sale',
  value: 271568.09,
  percent: 25.5,
  increment: 15
}

]

  return (
    <>
    <Header/>

    <div className="Dashboard_container">
        <SideBar />

     <h1>Welcome Back, Wahab</h1>
     <p>Here's what's happening with your store today.</p>
     <section className="Dashboard_Card_Container">
      
      {
        cardArray.map((obj, index)=>(
          <article  
          key={index}   
          onClick={()=> {
            setActive(index)
          }}
          className={Active === index? 'Blue_Card': ''}
          >
            <span>
              <div>{obj.icon}</div>
              <h4>{obj.title}</h4>
            </span>
            <h3>{obj.title === 'Total Sales' ? `$${obj.value}`: obj.value }</h3>
            <span>
              <p className="Card_percentage">{`${obj.percent}%`}</p>
              <p>{`+${obj.increment}k Today`}</p>
            </span>
          </article>
        ))
      }
      
     </section>
     <section className="Graph_Container">
      <div className="Main_Graph_Container">
        <span>
        <h3>Recent Orders</h3>
        <p>View All</p>
        </span>
        <span className="Graph_Subheader">
          <h4>Name</h4>
          <ul>
            <li>ID</li>
            <li>Price</li>
            <li>Amount</li>
            <li>Status</li>
          </ul>
        </span>
        <article>
          <span className="Dashboard_Order_Item">
            <div className="Dashboard_Order_Item_Description">
              <span className="Item_Img_Holder">
                <img src={LaptopImg} alt="a laptop" />
              </span>
              <span>
               <h2>HP EliteBook 830 Touchscreen</h2>
               <h4>Computing</h4>
              </span>
            </div>
            <div>
               <p>8976TY</p>
                <p>$30</p>
                <p>5,951</p>
                <p>Delivered</p>
            </div>
          </span>
        </article>
      </div>
      <div className="Side_Graph_Container"></div>
     </section>
     <section className="Bottom_Graph_Container"></section>

    </div>
    </>
  )
}
