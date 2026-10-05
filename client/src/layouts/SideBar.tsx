import { FC } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { sidebarItems } from '../utils/sidebar';

const Sidebar: FC = () => {
  const location = useLocation();
  const nav = useNavigate();

  const activeIndex = sidebarItems.findIndex((item) =>
    location.pathname.split('/').includes(item.itemName),
  );
  const currentIndex = activeIndex === -1 && location.pathname === '/' ? 0 : activeIndex;

  const handleClick = (_index: number, itemName: string) => {
    nav(`/${itemName}`);
  };

  return (
    <nav className="Home_Sidebar" aria-label="Main navigation">
      <p className="Sidebar_Section_Label">WORKSPACE</p>
      <div className="Sidebar_Container">
        {sidebarItems.map((item, index) => (
          <button
            key={item.itemName}
            type="button"
            onClick={() => handleClick(index, item.itemName)}
            className={currentIndex === index ? "Active_List" : ""}
            aria-current={currentIndex === index ? "page" : undefined}
          >
            <span className="List_icon" aria-hidden="true">{item.icon}</span>
            <span className="Sidebar_Item_Name">
              {item.itemName.charAt(0).toUpperCase() + item.itemName.slice(1)}
            </span>
          </button>
        ))}
      </div>
      <div className="Sidebar_Footer">
        <span className="Sidebar_Footer_Orb" />
        <div>
          <strong>Your workspace</strong>
          <span>Everything in one place</span>
        </div>
      </div>
    </nav>
  );
};

export default Sidebar;
