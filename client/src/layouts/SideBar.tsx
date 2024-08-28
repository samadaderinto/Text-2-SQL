import { FC } from 'react';
import { IoPeopleOutline, IoSettingsOutline } from "react-icons/io5";
import { RiShoppingBag3Line, RiLogoutBoxLine } from "react-icons/ri";
import { MdOutlineShoppingCart } from "react-icons/md";
import { RxDashboard } from 'react-icons/rx';
import { useNavigate, useLocation } from 'react-router-dom';
import { SideBarProps } from '../types/sidebar';
import { sideBarArrayList } from '../utils/sidebar';

const SideBar: FC = () => {
  const location = useLocation();
  const nav  = useNavigate();

  // Determine the current path segment
  const currentPath = location.pathname.split('/').filter(Boolean);
  const currentPathSegment = currentPath.length ? currentPath[currentPath.length - 1] : 'dashboard';

  // Define the sidebar item

  // Determine the index of the active item
  const activeIndex = sideBarArrayList.findIndex(item => item.itemName === currentPathSegment);

  const handleClick = (_index: number, itemName: string) => {
    nav(`/${itemName}`);
  };

  return (
    <div>
      <nav className="Home_Sidebar">
        <div className="Sidebar_Container">
          {sideBarArrayList.map((obj, index) => (
            <span
              key={index}
              onClick={() => handleClick(index, obj.itemName)}
              className={activeIndex === index ? 'Active_List' : ''}
            >
              <p className="List_icon">{obj.icon}</p>
              <p>{obj.itemName}</p>
            </span>
          ))}
        </div>
      </nav>
    </div>
  );
};

export default SideBar;
