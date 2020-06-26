import React from 'react';
import { compose } from 'redux';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import { Drawer, Position } from '@blueprintjs/core';
import { isLangRtl } from '@alephdata/react-ftm';

import EntityContextLoader from 'src/components/Entity/EntityContextLoader';
import EntityHeading from 'src/components/Entity/EntityHeading';
import EntityToolbar from 'src/components/Entity/EntityToolbar';
import EntityViews from 'src/components/Entity/EntityViews';
import { SectionLoading, ErrorSection } from 'src/components/common';
import { selectEntity, selectEntityView, selectLocale } from 'src/selectors';
import queryString from 'query-string';
import togglePreview from 'src/util/togglePreview';

import 'src/components/common/ItemOverview.scss';
import './EntityPreview.scss';


export class EntityPreview extends React.Component {
  constructor(props) {
    super(props);
    this.onClose = this.onClose.bind(this);
  }

  onClose(event) {
    // don't close preview if other entity label is clicked
    if (event.target.classList.contains('EntityLabel')) {
      return;
    }
    togglePreview(this.props.history, null);
  }

  renderContext() {
    const { entity, activeMode } = this.props;
    if (entity.isError) {
      return <ErrorSection error={entity.error} />;
    }
    if (entity.isPending) {
      return <SectionLoading />;
    }
    return (
      <div className="ItemOverview preview">
        <div className="ItemOverview__heading">
          <EntityHeading entity={entity} isPreview />
        </div>
        <div className="ItemOverview__content">
          <EntityViews entity={entity} activeMode={activeMode} isPreview />
        </div>
      </div>
    );
  }

  render() {
    const { entityId, entity, hidden, locale } = this.props;
    if (!entityId) {
      return null;
    }
    const drawerPos = isLangRtl(locale) ? Position.LEFT : Position.RIGHT;
    return (
      <EntityContextLoader entityId={entityId}>
        <Drawer
          className="EntityPreview"
          isOpen={!hidden}
          title={<EntityToolbar entity={entity} />}
          onClose={this.onClose}
          hasBackdrop={false}
          autoFocus={false}
          enforceFocus={false}
          position={drawerPos}
          // canOutsideClickClose={false}
          portalClassName="EntityPreview__overlay-container"
        >
          <div className="EntityPreview__content">
            {this.renderContext()}
          </div>
        </Drawer>
      </EntityContextLoader>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  const parsedHash = queryString.parse(ownProps.location.hash);
  const entityId = parsedHash['preview:id'];
  const activeMode = parsedHash['preview:mode'];
  return {
    entityId,
    parsedHash,
    entity: selectEntity(state, entityId),
    activeMode: selectEntityView(state, entityId, activeMode, true),
    locale: selectLocale(state),
  };
};

export default compose(
  withRouter,
  connect(mapStateToProps),
)(EntityPreview);
