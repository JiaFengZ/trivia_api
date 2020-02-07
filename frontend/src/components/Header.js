import React, { Component } from 'react';
import logo from '../logo.svg';
import '../stylesheets/Header.css';

class Header extends Component {
  navTo(uri){
    window.location.href = window.location.origin + uri;
  }
  getActiveNav () {
    return window.location.pathname
  }

  render() {
    const pathname = this.getActiveNav()
    return (
      <div className="App-header">
        <h1 onClick={() => {this.navTo('')}}>Udacitrivia</h1>
        <h2 onClick={() => {this.navTo('')}} className={pathname === '/' ? 'active' : ''}>List</h2>
        <h2 onClick={() => {this.navTo('/add')}} className={pathname === '/add' ? 'active' : ''}>Add</h2>
        <h2 onClick={() => {this.navTo('/play')}} className={pathname === '/play' ? 'active' : ''}>Play</h2>
      </div>
    );
  }
}

export default Header;
