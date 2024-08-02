import { ReactElement, useState  } from "react";
import {  HiOutlineChartSquareBar } from 'react-icons/hi'
import {  RiShoppingBag4Line } from 'react-icons/ri'
import { GoContainer } from "react-icons/go";
import {  IoPeopleOutline  } from 'react-icons/io5'

export const Dashboard = () => {

  const  [Active, setActive] = useState< number | null>(null)

interface card {
  icon: ReactElement,
  title: string,
  value: number,
  percent: number,
  increment: number
}

const cardArray: card[] = [

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
  title: 'Total Salesrt',
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
    <div className="Dashboard_container">
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
      <div className="Main_Graph_Container"></div>
      <div className="Side_Graph_Container"></div>
     </section>
    </div>
  )
}
