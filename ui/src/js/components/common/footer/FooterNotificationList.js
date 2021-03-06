// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
import Moment from 'moment';

// store
import { setUpdateHistoryView } from 'JS/redux/reducers/footer';


export default class FooterNotificationList extends Component {
  render() {
    const messageList = this.props.parentState.viewHistory ? this.props.parentState.messageStackHistory : this.props.parentState.messageStack;

    const messageListOpenItems = messageList.filter(message => message.messageBodyOpen);

    const footerMessageSectionClass = classNames({
      'Footer__messages-section': true,
      'Footer__messages-section--collapsed': !this.props.parentState.messageListOpen,
      'Footer__message-section--helper-open': this.props.parentState.helperVisible,
    });

    const footerMessageListClass = classNames({
      'Footer__message-list': true,
      'Footer__message-list--collapsed': !this.props.parentState.messageListOpen,
    });

    const viewAllButtonClass = classNames({
      'Footer__button--view-all': true,
      hidden: (this.props.parentState.viewHistory || !this.props.parentState.messageListOpen),
    });

    let height = messageList.length > 6 ? 260 : messageList.length * 60;
    height = messageListOpenItems.length > 0 ? 'auto' : height;

    height = height === 'auto' ? 'auto' : `${height}px`;


    return (
      <div className={footerMessageSectionClass}>
        <div
          className={viewAllButtonClass}
          onClick={() => setUpdateHistoryView()}
        >
          View All
        </div>
        <div className={footerMessageListClass} style={{ height, maxHeight: '700px' }}>

          <ul>
            {
              messageList.map((messageItem, index) => {
                const messageBodyClasses = classNames({
                  'Footer__message-body-content': true,
                  hidden: !messageItem.messageBodyOpen,
                });

                const toggleButton = classNames({
                  'Footer__button--toggle': true,
                  open: messageItem.messageBodyOpen,
                });

                const bodyCSS = classNames({
                  'Footer__body-height': messageItem.messageBodyOpen,
                  [messageItem.className]: true,
                });
                const messageTitleCSS = classNames({
                  'Footer__message-title': true,
                  'Footer__message-title--collapsed': !messageItem.messageBodyOpen,
                });
                return (
                  <li
                    key={messageItem.id + index}
                    className={bodyCSS}
                  >
                    <div className="Footer__message-body">
                      <div className="Footer__flex-container">
                        <div className="Footer__message-icon" />

                        <div className="Footer__message-time">{Moment(messageItem.date).fromNow()}:</div>
                        <div className="Footer__message-item">
                          <p className={messageTitleCSS}>
                            {messageItem.message}
                          </p>
                        </div>

                        { (messageItem.messageBody.length > 0) &&
                          <div className="Footer__message-expand">
                            <div
                              className={toggleButton}
                              onClick={() => { this.props.showMessageBody(index); }}
                            />
                          </div>

                        }
                      </div>

                      <div className={messageBodyClasses}>

                        <ul>
                          {
                            messageItem.messageBody && messageItem.messageBody.map((item, index) => (
                              <li
                                key={messageItem.id + index}
                              >
                                <div className="Footer__message-body-content--text" dangerouslySetInnerHTML={{ __html: item.message }} />
                              </li>))
                          }
                        </ul>
                      </div>
                    </div>

                  </li>);
                })
              }

            {
                  (messageList.length === 0) &&

                  <li

                    className="Footer__message"
                  >
                    <div className="Footer__message-body">
                      <div className="Footer__flex-container">

                        <div className="Footer__message-item">
                          <p className="Footer__message-title">
                            No Notifications
                          </p>
                        </div>
                      </div>
                    </div>
                  </li>
               }

          </ul>
        </div>
      </div>
    );
  }
}
