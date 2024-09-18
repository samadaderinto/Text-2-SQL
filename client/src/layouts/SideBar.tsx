import { FC } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { sideBarArrayList } from '../utils/sidebar';

const SideBar: FC = () => {
  const location = useLocation();
  const nav = useNavigate();

  const currentPath = location.pathname.split('/').filter(Boolean);
  const currentPathSegment = currentPath.length ? currentPath[currentPath.length - 1] : 'dashboard';


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
