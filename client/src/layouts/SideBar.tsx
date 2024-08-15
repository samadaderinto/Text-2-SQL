import { FC, useState } from 'react'
import { IoPeopleOutline, IoSettingsOutline } from "react-icons/io5";
import { RiShoppingBag3Line } from "react-icons/ri";
import { RxDashboard } from 'react-icons/rx'
import { RiLogoutBoxLine } from "react-icons/ri";
import { MdOutlineShoppingCart } from "react-icons/md";
import { useNavigate } from 'react-router-dom';
import { SideBarProps } from '../types/sidebar';

const SideBar: FC = () => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  const [active, setActive] = useState('Dashboard')
  const Nav = useNavigate()


  

  const sideBarArrayList: SideBarProps[] = [
    {
      icon: <RxDashboard />,
      itemName: 'dashboard'
    },
    {
      icon: <RiShoppingBag3Line />,
      itemName: 'product'
    },
    {
      icon: <MdOutlineShoppingCart />,
      itemName: 'orders'
    },
    {
      icon: <IoPeopleOutline />,
      itemName: 'customers'
    },
    {
      icon: <IoSettingsOutline />,
      itemName: 'settings'
    },
    {
      icon: <RiLogoutBoxLine />,
      itemName: 'logout'
    }
  ]


  return (
    <div>
      <nav className="Home_Sidebar">
        <div className="Sidebar_Container">

          {
            sideBarArrayList.map((obj, index) => (
              <span
                key={index}
                onClick={() => {
                  setActive(obj.itemName)
                  setActiveIndex(index)
                  Nav(`/${obj.itemName}`)

                }}
                className={activeIndex === index ? 'Active_List' : ''}>
                <p className="List_icon">{obj.icon}</p>
                <p>{obj.itemName}</p>
              </span>
            ))


          }

        </div>
      </nav>
    </div>
  )
}


export default SideBar;
