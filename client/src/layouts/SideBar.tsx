import { FC } from 'react';
import { IoPeopleOutline, IoSettingsOutline } from "react-icons/io5";
import { RiShoppingBag3Line, RiLogoutBoxLine } from "react-icons/ri";
import { MdOutlineShoppingCart } from "react-icons/md";
import { RxDashboard } from 'react-icons/rx';
import { useNavigate, useLocation } from 'react-router-dom';
import { SideBarProps } from '../types/sidebar';

const SideBar: FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Determine the current path segment
  const currentPath = location.pathname.split('/').filter(Boolean);
  const currentPathSegment = currentPath.length ? currentPath[currentPath.length - 1] : 'dashboard';

  // Define the sidebar items
  const sideBarArrayList: SideBarProps[] = [
    { icon: <RxDashboard />, itemName: 'dashboard' },
    { icon: <RiShoppingBag3Line />, itemName: 'product' },
    { icon: <MdOutlineShoppingCart />, itemName: 'orders' },
    { icon: <IoPeopleOutline />, itemName: 'customers' },
    { icon: <IoSettingsOutline />, itemName: 'settings' },
    { icon: <RiLogoutBoxLine />, itemName: 'logout' }
  ];

  // Determine the index of the active item
  const activeIndex = sideBarArrayList.findIndex(item => item.itemName === currentPathSegment);

  const handleClick = (index: number, itemName: string) => {
    navigate(`/${itemName}`);
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
